
import os
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    CallbackQueryHandler,
    ConversationHandler
)
from handlers.user import start, name, uid, email, problem
from handlers.agent import start_agent, agent_message, button_handler

# Environment variables from Render
BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
PORT = int(os.environ.get("PORT", 10000))  # Render provides this automatically

# Build the bot application
app = ApplicationBuilder().token(BOT_TOKEN).build()

# User ConversationHandler (FSM for ticket creation)
conv_handler = ConversationHandler(
    entry_points=[CommandHandler("start", start)],
    states={
        0: [MessageHandler(filters.TEXT, name)],
        1: [MessageHandler(filters.TEXT, uid)],
        2: [MessageHandler(filters.TEXT, email)],
        3: [MessageHandler(filters.TEXT | filters.PHOTO | filters.VIDEO | filters.ANIMATION, problem)]
    },
    fallbacks=[]
)
app.add_handler(conv_handler)

# Agent handlers
app.add_handler(CommandHandler("agent", start_agent))
app.add_handler(MessageHandler(filters.TEXT | filters.PHOTO | filters.VIDEO | filters.ANIMATION, agent_message))
app.add_handler(CallbackQueryHandler(button_handler))

# Start webhook for Render
app.run_webhook(
    listen="0.0.0.0",
    port=PORT,
    url_path=BOT_TOKEN,
    webhook_url=f"{WEBHOOK_URL}/{BOT_TOKEN}"
)
