import logging
import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
from flask import Flask, request
from config import BOT_TOKEN
from database import init_db
from handlers import user, agent, admin

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Initialize database
init_db()

# Telegram bot
telegram_app = ApplicationBuilder().token(BOT_TOKEN).build()

# User Handlers
telegram_app.add_handler(CommandHandler("start", user.start))
telegram_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, user.handle_message))

# Agent Handlers
telegram_app.add_handler(CommandHandler("cases", agent.list_cases))
telegram_app.add_handler(CommandHandler("reply", agent.reply_case))

# Admin Handlers
telegram_app.add_handler(CommandHandler("addagent", admin.add_agent))
telegram_app.add_handler(CommandHandler("removeagent", admin.remove_agent))

# Flask app for webhook
app = Flask(__name__)

@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), telegram_app.bot)
    telegram_app.update_queue.put(update)
    return "ok"

if __name__ == "__main__":
    # Set webhook (replace with your public Railway URL)
    RAILWAY_URL = "https://bifinance-cs-bot.up.railway.app"  # ← replace with your live Railway URL
    telegram_app.bot.set_webhook(f"{RAILWAY_URL}/{BOT_TOKEN}")

    print("🤖 Bot is running on Railway...")
    app.run(port=5000)
