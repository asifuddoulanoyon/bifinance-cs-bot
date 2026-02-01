import os
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters
)
import handlers.user as user
import handlers.agent as agent
import handlers.admin as admin

# Load environment variables
TOKEN = os.getenv("BOT_TOKEN")
OWNER_ID = int(os.getenv("OWNER_ID"))

def main():
    # Create application
    app = ApplicationBuilder().token(TOKEN).build()

    # ---------------- Commands ----------------
    # User commands
    app.add_handler(CommandHandler("start", user.start))
    app.add_handler(CommandHandler("help", user.help_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, user.handle_user_message))

    # Agent commands
    app.add_handler(CommandHandler("cases", agent.show_cases))
    app.add_handler(CallbackQueryHandler(agent.button_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, agent.handle_agent_reply))
    app.add_handler(CommandHandler("transfer", agent.transfer_case))
    app.add_handler(CommandHandler("close", agent.close_case))

    # Admin commands
    app.add_handler(CommandHandler("addagent", admin.add_agent))
    app.add_handler(CommandHandler("removeagent", admin.remove_agent))

    # Start polling
    print("🤖 Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()def main():
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
