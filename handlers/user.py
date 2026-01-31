from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler, MessageHandler, filters
import random
from database import c, conn

NAME, UID, EMAIL, PROBLEM = range(4)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("Create Ticket", callback_data="create_ticket")]]
    markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("👋 Welcome! Click below to create a ticket:", reply_markup=markup)

async def user_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "create_ticket":
        await query.message.reply_text("Enter your *Name*:", parse_mode="Markdown")
        return NAME
    elif query.data.startswith("rate_"):
        parts = query.data.split("_")
        case_id = parts[1]
        rating = int(parts[2])
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
    name_val = context.user_data["name"]
    uid_val = context.user_data["uid"]
    email_val = context.user_data["email"]

    c.execute(
        "INSERT INTO cases (case_id, user_id, name, uid, email, problem, status, conversation) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (case_id, user_id, name_val, uid_val, email_val, text, "OPEN", text)
    )
    conn.commit()

    await update.message.reply_text(f"✅ Ticket created! Case ID: {case_id}")

    # Notify agents
    from config import AGENTS
    for agent_id in AGENTS:
        try:
            await context.bot.send_message(agent_id, f"📌 New ticket: {case_id}\nUser: {name_val}")
        except: pass

    return ConversationHandler.END
