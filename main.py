import os
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, ConversationHandler, filters
from handlers.user import start, user_button, name, uid, email, problem, NAME, UID, EMAIL, PROBLEM
from handlers.agent import show_agent_panel, agent_button
from config import BOT_OWNER_ID, AGENTS, BOT_TOKEN, WEBHOOK_URL

PORT = int(os.environ.get("PORT", 10000))

app = ApplicationBuilder().token(BOT_TOKEN).build()

conv_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(user_button, pattern="^create_ticket$")],
    states={
        NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, name)],
        UID: [MessageHandler(filters.TEXT & ~filters.COMMAND, uid)],
        EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, email)],
        PROBLEM: [MessageHandler(filters.TEXT | filters.PHOTO | filters.VIDEO | filters.ANIMATION | filters.Document.ALL, problem)]
    },
    fallbacks=[]
)

app.add_handler(conv_handler)
app.add_handler(CallbackQueryHandler(user_button, pattern="^(my_tickets|ticket_|agent_panel|rate_)"))
app.add_handler(CallbackQueryHandler(agent_button, pattern="^(case_|transfer_|close)"))
app.add_handler(CommandHandler("start", start))

# Owner commands
async def add_agent(update, context):
    if update.message.from_user.id != BOT_OWNER_ID:
        await update.message.reply_text("Not authorized")
        return
    if not context.args:
        await update.message.reply_text("Usage: /addagent <user_id>")
        return
    AGENTS.append(int(context.args[0]))
    await update.message.reply_text(f"Added agent {context.args[0]}")

async def remove_agent(update, context):
    if update.message.from_user.id != BOT_OWNER_ID:
        await update.message.reply_text("Not authorized")
        return
    if not context.args:
        await update.message.reply_text("Usage: /removeagent <user_id>")
        return
    AGENTS.remove(int(context.args[0]))
    await update.message.reply_text(f"Removed agent {context.args[0]}")

app.add_handler(CommandHandler("addagent", add_agent))
app.add_handler(CommandHandler("removeagent", remove_agent))

# Run webhook for Render
app.run_webhook(
    listen="0.0.0.0",
    port=PORT,
    url_path=BOT_TOKEN,
    webhook_url=f"{WEBHOOK_URL}/{BOT_TOKEN}"
)
