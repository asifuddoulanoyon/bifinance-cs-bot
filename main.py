from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

BOT_TOKEN = "8265176097:AAHL_ULGDtfO3-HAoayOfIBNJhU9oPJtDqE"


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ Bot is alive and working!")


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(update.message.text)


def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    print("🤖 Bot started...")
    app.run_polling()


if __name__ == "__main__":
    main()if __name__ == "__main__":
    main()        update = Update.de_json(request.get_json(force=True), app.bot)
        app.update_queue.put(update)
        return "ok"

    # Start Flask app
    flask_app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
