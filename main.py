import os
from telegram.ext import ApplicationBuilder, CommandHandler, ConversationHandler, MessageHandler, filters
from handlers.user import start, user_message, create_ticket_start, NAME, UID, EMAIL, PROBLEM, name, uid, email, problem

from config import BOT_TOKEN, WEBHOOK_URL, BOT_OWNER_ID

PORT = int(os.environ.get("PORT", 10000))

app = ApplicationBuilder().token(BOT_TOKEN).build()

conv_handler = ConversationHandler(
    entry_points=[CommandHandler("start", create_ticket_start)],
    states={
        NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, name)],
        UID: [MessageHandler(filters.TEXT & ~filters.COMMAND, uid)],
        EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, email)],
        PROBLEM: [MessageHandler(filters.TEXT & ~filters.COMMAND, problem)]
    },
    fallbacks=[]
)

app.add_handler(conv_handler)
app.add_handler(MessageHandler(filters.TEXT | filters.PHOTO | filters.VIDEO | filters.Document.ALL, user_message))
app.add_handler(CommandHandler("start", start))

app.run_webhook(
    listen="0.0.0.0",
    port=PORT,
    url_path=BOT_TOKEN,
    webhook_url=f"{WEBHOOK_URL}/{BOT_TOKEN}"
)
