import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    CallbackQueryHandler,
    ContextTypes,
    ConversationHandler
)
import sqlite3
import random
import datetime

# === CONFIG ===
BOT_OWNER_ID = 1675295056
BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
PORT = int(os.environ.get("PORT", 10000))

# Database
conn = sqlite3.connect("support.db", check_same_thread=False)
c = conn.cursor()

# Create table if not exists
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
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
''')
conn.commit()

# States
NAME, UID, EMAIL, PROBLEM = range(4)

# ================== USER HANDLERS ==================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 *Welcome to Bifinance Customer Support!*\nPlease enter your *Name*: ", parse_mode="Markdown")
    return NAME

async def name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["name"] = update.message.text
    await update.message.reply_text("Enter your *Bifinance UID* (or type skip):", parse_mode="Markdown")
    return UID

async def uid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    context.user_data["uid"] = None if text.lower() == "skip" else text
    await update.message.reply_text("Enter your *email*:", parse_mode="Markdown")
    return EMAIL

async def email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if "@" not in text:
        await update.message.reply_text("❌ Invalid email, try again:")
        return EMAIL
    context.user_data["email"] = text
    await update.message.reply_text("Please describe your *problem*: ", parse_mode="Markdown")
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

    await update.message.reply_text(f"✅ Your support ticket is created!\n*Case ID:* {case_id}", parse_mode="Markdown")

    # Notify all agents
    c.execute("SELECT assigned_agent FROM cases WHERE status='OPEN'")
    agents = set(row[0] for row in c.fetchall() if row[0])
    for agent_id in agents:
        try:
            await context.bot.send_message(agent_id, f"📌 New ticket created!\n*Case ID:* {case_id}\nUser: {name}", parse_mode="Markdown")
        except:
            pass

    return ConversationHandler.END

# ================== AGENT HANDLERS ==================

async def start_agent(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id != BOT_OWNER_ID and user_id not in context.bot_data.get("agents", []):
        await update.message.reply_text("❌ You are not authorized as an agent.")
        return
    await update.message.reply_text("👨‍💼 Agent Panel Activated\nUse the buttons below to manage cases.", parse_mode="Markdown")

async def agent_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Placeholder for agent replying logic
    await update.message.reply_text("Agent message received. Reply logic will be implemented.")

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
