import os, random, sqlite3
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, filters,
    CallbackQueryHandler, ConversationHandler, ContextTypes
)
from config import BOT_OWNER_ID, AGENTS

# Environment
BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
PORT = int(os.environ.get("PORT", 10000))

# Database
conn = sqlite3.connect("support.db", check_same_thread=False)
c = conn.cursor()
c.execute('''
CREATE TABLE IF NOT EXISTS cases (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    case_id TEXT,
    user_id INTEGER,
    name TEXT,
    uid TEXT,
    email TEXT,
    problem TEXT,
    status TEXT,
    assigned_agent INTEGER,
    conversation TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    rating INTEGER
)
''')
conn.commit()

# User conversation states
NAME, UID, EMAIL, PROBLEM = range(4)

# ======= USER HANDLERS =======
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("Create Ticket", callback_data="create_ticket")]]
    markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("👋 Welcome! Use the button below to create a ticket:", reply_markup=markup)

async def user_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "create_ticket":
        await query.message.reply_text("Please enter your *Name*:", parse_mode="Markdown")
        return NAME
    elif query.data.startswith("rate_"):
        case_id = query.data.split("_")[1]
        rating = int(query.data.split("_")[2])
        c.execute("UPDATE cases SET rating=? WHERE case_id=?", (rating, case_id))
        conn.commit()
        await query.message.reply_text(f"Thank you! You rated {rating}⭐")
        return ConversationHandler.END

async def name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["name"] = update.message.text
    await update.message.reply_text("Enter your UID (or type skip):")
    return UID

async def uid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    context.user_data["uid"] = None if text.lower() == "skip" else text
    await update.message.reply_text("Enter your email:")
    return EMAIL

async def email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if "@" not in text:
        await update.message.reply_text("Invalid email, try again:")
        return EMAIL
    context.user_data["email"] = text
    await update.message.reply_text("Describe your problem:")
    return PROBLEM

async def problem(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text or "Media sent"
    case_id = f"BF-{random.randint(100000,999999)}"
    user_id = update.message.from_user.id
    name = context.user_data["name"]
    uid_val = context.user_data["uid"]
    email_val = context.user_data["email"]

    c.execute(
        "INSERT INTO cases (case_id, user_id, name, uid, email, problem, status, conversation) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (case_id, user_id, name, uid_val, email_val, text, "OPEN", text)
    )
    conn.commit()

    await update.message.reply_text(f"✅ Ticket created! Case ID: {case_id}")

    # Notify all agents
    for agent_id in AGENTS:
        try:
            await context.bot.send_message(agent_id, f"📌 New ticket: {case_id}\nUser: {name}")
        except: pass

    return ConversationHandler.END

# ======= AGENT HANDLERS =======
async def start_agent(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id != BOT_OWNER_ID and user_id not in AGENTS:
        await update.message.reply_text("❌ You are not authorized as agent.")
        return
    await show_agent_panel(update, context)

async def show_agent_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    agent_id = update.message.from_user.id
    c.execute("SELECT case_id, status FROM cases WHERE assigned_agent=? OR assigned_agent IS NULL", (agent_id,))
    cases = c.fetchall()
    buttons = [[InlineKeyboardButton(f"{c_id} - {status}", callback_data=f"case_{c_id}")] for c_id, status in cases]
    markup = InlineKeyboardMarkup(buttons) if buttons else None
    await update.message.reply_text("📂 Your Tickets:", reply_markup=markup or None)

async def agent_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    if data.startswith("case_"):
        case_id = data.split("_")[1]
        context.user_data["current_case"] = case_id
        c.execute("SELECT problem, status FROM cases WHERE case_id=?", (case_id,))
        prob, status = c.fetchone()
        keyboard = [
            [InlineKeyboardButton("Transfer", callback_data="transfer"), InlineKeyboardButton("Close", callback_data="close")]
        ]
        markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(f"📝 {case_id}\nStatus: {status}\nProblem: {prob}", reply_markup=markup)
    elif data == "transfer":
        keyboard = [[InlineKeyboardButton(str(aid), callback_data=f"transfer_{aid}")] for aid in AGENTS]
        await query.edit_message_text("Select agent to transfer:", reply_markup=InlineKeyboardMarkup(keyboard))
    elif data.startswith("transfer_"):
        new_agent = int(data.split("_")[1])
        case_id = context.user_data["current_case"]
        c.execute("UPDATE cases SET assigned_agent=? WHERE case_id=?", (new_agent, case_id))
        conn.commit()
        await query.edit_message_text(f"✅ Ticket {case_id} transferred to agent {new_agent}")
    elif data == "close":
        case_id = context.user_data["current_case"]
        c.execute("UPDATE cases SET status='CLOSED' WHERE case_id=?", (case_id,))
        conn.commit()
        # Notify user
        c.execute("SELECT user_id FROM cases WHERE case_id=?", (case_id,))
        user_id = c.fetchone()[0]
        keyboard = [
            [InlineKeyboardButton(str(i), callback_data=f"rate_{case_id}_{i}")] for i in range(1, 6)
        ]
        await context.bot.send_message(user_id, "✅ Your ticket is closed! Please rate the agent:", reply_markup=InlineKeyboardMarkup(keyboard))
        await query.edit_message_text(f"✅ Ticket {case_id} closed")

async def agent_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if "current_case" not in context.user_data:
        await update.message.reply_text("Select a ticket first.")
        return
    case_id = context.user_data["current_case"]
    text = update.message.text or "Media sent"
    c.execute("UPDATE cases SET conversation = conversation || '\nAgent: " + text + "' WHERE case_id=?", (case_id,))
    conn.commit()
    # Send to user
    c.execute("SELECT user_id FROM cases WHERE case_id=?", (case_id,))
    user_id = c.fetchone()[0]
    try:
        await context.bot.send_message(user_id, f"💬 Agent replied:\n{text}")
    except: pass
    await update.message.reply_text("Message sent to user.")

# ======= OWNER COMMANDS =======
async def add_agent(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != BOT_OWNER_ID:
        await update.message.reply_text("❌ Only owner can add agents.")
        return
    if not context.args:
        await update.message.reply_text("Usage: /addagent <user_id>")
        return
    AGENTS.append(int(context.args[0]))
    await update.message.reply_text(f"✅ Added agent {context.args[0]}")

async def remove_agent(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != BOT_OWNER_ID:
        await update.message.reply_text("❌ Only owner can remove agents.")
        return
    if not context.args:
        await update.message.reply_text("Usage: /removeagent <user_id>")
        return
    AGENTS.remove(int(context.args[0]))
    await update.message.reply_text(f"✅ Removed agent {context.args[0]}")

# ======= APPLICATION =======
app = ApplicationBuilder().token(BOT_TOKEN).build()

# User conversation handler
conv_handler = ConversationHandler(
    entry_points=[CommandHandler("start", start)],
    states={
        NAME: [MessageHandler(filters.TEXT, name)],
        UID: [MessageHandler(filters.TEXT, lambda u,c: uid(u,c))],
        EMAIL: [MessageHandler(filters.TEXT, email)],
        PROBLEM: [MessageHandler(filters.TEXT | filters.PHOTO | filters.VIDEO | filters.ANIMATION, problem)]
    },
    fallbacks=[]
)
app.add_handler(conv_handler)

# User buttons
app.add_handler(CallbackQueryHandler(user_button, pattern="^(create_ticket|rate_)"))

# Agent handlers
app.add_handler(CommandHandler("agent", start_agent))
app.add_handler(MessageHandler(filters.TEXT | filters.PHOTO | filters.VIDEO | filters.ANIMATION, agent_message))
app.add_handler(CallbackQueryHandler(agent_button, pattern="^(case_|transfer_|close)"))

# Owner commands
app.add_handler(CommandHandler("addagent", add_agent))
app.add_handler(CommandHandler("removeagent", remove_agent))

# ======= WEBHOOK =======
app.run_webhook(
    listen="0.0.0.0",
    port=PORT,
    url_path=BOT_TOKEN,
    webhook_url=f"{WEBHOOK_URL}/{BOT_TOKEN}"
)    await update.message.reply_text("Agent message received. Reply logic will be implemented.")

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(text=f"Button pressed: {query.data}")

# ================== MAIN ==================

app = ApplicationBuilder().token(BOT_TOKEN).build()

# User conversation handler
conv_handler = ConversationHandler(
    entry_points=[CommandHandler("start", start)],
    states={
        NAME: [MessageHandler(filters.TEXT, name)],
        UID: [MessageHandler(filters.TEXT, uid)],
        EMAIL: [MessageHandler(filters.TEXT, email)],
        PROBLEM: [MessageHandler(filters.TEXT | filters.PHOTO | filters.VIDEO | filters.ANIMATION, problem)]
    },
    fallbacks=[]
)
app.add_handler(conv_handler)

# Agent handlers
app.add_handler(CommandHandler("agent", start_agent))
app.add_handler(MessageHandler(filters.TEXT | filters.PHOTO | filters.VIDEO | filters.ANIMATION, agent_message))
app.add_handler(CallbackQueryHandler(button_handler))

# Webhook setup for Render
app.run_webhook(
    listen="0.0.0.0",
    port=PORT,
    url_path=BOT_TOKEN,
    webhook_url=f"{WEBHOOK_URL}/{BOT_TOKEN}"
)
