import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
from config import BOT_TOKEN, OWNER_ID
from handlers import user, agent, admin

PORT = int(os.environ.get("PORT", 3000))  # Railway sets PORT automatically

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 Bifinance Customer Support Bot is online!\nUse /help for instructions."
    )

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Command handlers
    app.add_handler(CommandHandler("start", start))

    # User handlers
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, user.handle_user_message))

    # Agent handlers
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, agent.handle_agent_message))

    # Admin handlers
    app.add_handler(CommandHandler("addagent", admin.add_agent))
    app.add_handler(CommandHandler("removeagent", admin.remove_agent))

    print("🤖 Bot is running on Railway...")
    app.run_polling()  # for now, we can switch to webhook later

if __name__ == "__main__":
    main()        )

# ---------------- MAIN FUNCTION ----------------
def main():
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
