import os
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters
)
import handlers.user as user
import handlers.agent as agent
import handlers.admin as admin

TOKEN = os.getenv("BOT_TOKEN")
OWNER_ID = int(os.getenv("OWNER_ID"))

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    # ---- User Handlers ----
    app.add_handler(CommandHandler("start", user.start))
    app.add_handler(CommandHandler("help", user.help_command))
    app.add_handler(MessageHandler(filters.TEXT | filters.PHOTO | filters.VIDEO | filters.DOCUMENT | filters.ANIMATION, user.handle_user_message))

    # ---- Agent Handlers ----
    app.add_handler(CommandHandler("cases", agent.show_cases))
    app.add_handler(CallbackQueryHandler(agent.button_callback))
    app.add_handler(MessageHandler(filters.TEXT | filters.PHOTO | filters.VIDEO | filters.DOCUMENT | filters.ANIMATION, agent.handle_agent_reply))
    app.add_handler(CommandHandler("transfer", agent.transfer_case))
    app.add_handler(CommandHandler("close", agent.close_case))

    # ---- Admin Handlers ----
    app.add_handler(CommandHandler("addagent", admin.add_agent))
    app.add_handler(CommandHandler("removeagent", admin.remove_agent))

    print("🤖 Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
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
