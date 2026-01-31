import os
import sqlite3
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, filters,
    CallbackQueryHandler, ConversationHandler, ContextTypes
)
from handlers.user import start_user, user_message
from handlers.agent import agent_panel, agent_button, agent_reply, AGENT_REPLY
from config import BOT_OWNER_ID, AGENTS

# --- Database connection ---
conn = sqlite3.connect("support.db", check_same_thread=False)
c = conn.cursor()

# --- Bot token from environment ---
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    print("ERROR: BOT_TOKEN not set in environment")
    exit(1)

# --- Build application ---
app = ApplicationBuilder().token(BOT_TOKEN).build()

# ----------------------
# ADMIN COMMANDS
# ----------------------
async def add_agent(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != BOT_OWNER_ID:
        await update.message.reply_text("❌ Not authorized")
        return
    if not context.args:
        await update.message.reply_text("Usage: /addagent <user_id>")
        return
    AGENTS.append(int(context.args[0]))
    await update.message.reply_text(f"✅ Added agent {context.args[0]}")

async def remove_agent(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != BOT_OWNER_ID:
        await update.message.reply_text("❌ Not authorized")
        return
    if not context.args:
        await update.message.reply_text("Usage: /removeagent <user_id>")
        return
    AGENTS.remove(int(context.args[0]))
    await update.message.reply_text(f"✅ Removed agent {context.args[0]}")

app.add_handler(CommandHandler("addagent", add_agent))
app.add_handler(CommandHandler("removeagent", remove_agent))

# ----------------------
# USER HANDLERS
# ----------------------
app.add_handler(CommandHandler("start", start_user))
app.add_handler(MessageHandler(filters.ALL, user_message))

# ----------------------
# AGENT HANDLERS
# ----------------------
# Agent panel command
app.add_handler(CommandHandler("agent", agent_panel))

# Agent buttons: take, switch, reply, close, rate, transfer
app.add_handler(CallbackQueryHandler(agent_button, pattern="^(take_|switch_|reply_|close_|rate_|transfer_)"))

# Agent reply FSM
agent_conv = ConversationHandler(
    entry_points=[CallbackQueryHandler(agent_button, pattern="^reply_")],
    states={AGENT_REPLY: [MessageHandler(filters.TEXT | filters.PHOTO | filters.VIDEO | filters.Document.ALL, agent_reply)]},
    fallbacks=[]
)
app.add_handler(agent_conv)

# ----------------------
# HELP COMMAND
# ----------------------
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "🛡️ **Bifinance Customer Support Help**\n\n"
        "Users:\n"
        "/start - Create a new support ticket\n"
        "/help - Show this message\n\n"
        "Agents:\n"
        "/agent - Open agent panel\n"
        "Click buttons to take/reply/close/transfer cases\n\n"
        "Admins:\n"
        "/addagent <user_id> - Add agent\n"
        "/removeagent <user_id> - Remove agent"
    )
    await update.message.reply_text(text)

app.add_handler(CommandHandler("help", help_command))

# ----------------------
# RUN
# ----------------------
if __name__ == "__main__":
    # Use webhook for Render deployment
    from flask import Flask, request
    from telegram import Update
    from telegram.ext import Application

    WEBHOOK_URL = os.getenv("WEBHOOK_URL")
    if not WEBHOOK_URL:
        print("ERROR: WEBHOOK_URL not set in environment")
        exit(1)

    flask_app = Flask(__name__)

    @flask_app.route("/", methods=["POST"])
    def webhook():
        update = Update.de_json(request.get_json(force=True), app.bot)
        app.update_queue.put(update)
        return "ok"

    # Start Flask app
    flask_app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
