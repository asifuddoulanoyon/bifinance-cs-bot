import logging
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
from config import BOT_TOKEN
from database import init_db
from handlers import user, agent, admin

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

def main():
    init_db()

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # User commands
    app.add_handler(CommandHandler("start", user.start))
    app.add_handler(MessageHandler(filters.TEXT | filters.PHOTO | filters.VIDEO | filters.Document.ALL, user.handle_message))

    # Agent commands
    app.add_handler(CommandHandler("cases", agent.list_cases))
    app.add_handler(CommandHandler("reply", agent.reply_case))

    # Admin commands
    app.add_handler(CommandHandler("addagent", admin.add_agent))
    app.add_handler(CommandHandler("removeagent", admin.remove_agent))

    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()    main()def main():
    app = ApplicationBuilder().token(TOKEN).build()

    # Handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, check_username))

    print("🤖 Bot is running...")
    app.run_polling()

# ---------------- RUN ----------------
if __name__ == "__main__":
    main()
# ---------------- MAIN FUNCTION ----------------
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, check_username))

    print("🤖 Bot is running...")
    app.run_polling()

# ---------------- RUN ----------------
if __name__ == "__main__":
    main()
