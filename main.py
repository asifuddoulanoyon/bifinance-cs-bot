import os
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, filters,
    CallbackQueryHandler, ConversationHandler
)
from handlers.user import start, user_button, name, uid, email, problem, NAME, UID, EMAIL, PROBLEM
from handlers.agent import start_agent, agent_message, agent_button
from config import BOT_OWNER_ID, AGENTS

BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
PORT = int(os.environ.get("PORT", 10000))

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

# User buttons
app.add_handler(CallbackQueryHandler(user_button, pattern="^(create_ticket|rate_)"))

# Agent handlers
app.add_handler(CommandHandler("agent", start_agent))
app.add_handler(MessageHandler(filters.TEXT | filters.PHOTO | filters.VIDEO | filters.ANIMATION, agent_message))
app.add_handler(CallbackQueryHandler(agent_button, pattern="^(case_|transfer_|close)"))

# Owner commands
async def add_agent(update, context):
    if update.message.from_user.id != BOT_OWNER_ID:
        await update.message.reply_text("❌ Only owner can add agents.")
        return
    if not context.args:
        await update.message.reply_text("Usage: /addagent <user_id>")
        return
    AGENTS.append(int(context.args[0]))
    await update.message.reply_text(f"✅ Added agent {context.args[0]}")

async def remove_agent(update, context):
    if update.message.from_user.id != BOT_OWNER_ID:
        await update.message.reply_text("❌ Only owner can remove agents.")
        return
    if not context.args:
        await update.message.reply_text("Usage: /removeagent <user_id>")
        return
    AGENTS.remove(int(context.args[0]))
    await update.message.reply_text(f"✅ Removed agent {context.args[0]}")

app.add_handler(CommandHandler("addagent", add_agent))
app.add_handler(CommandHandler("removeagent", remove_agent))

# Run webhook
app.run_webhook(
    listen="0.0.0.0",
    port=PORT,
    url_path=BOT_TOKEN,
    webhook_url=f"{WEBHOOK_URL}/{BOT_TOKEN}"
)
