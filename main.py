import os
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    MessageHandler,
    filters,
)

TOKEN = os.getenv("BOT_TOKEN")

# ---------------- START COMMAND ----------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 Bot is online!\nAdd me to a group and try: ? @username"
    )

# ---------------- WELCOME MESSAGE ----------------
async def welcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Trigger for new chat members
    if update.message.new_chat_members:
        for member in update.message.new_chat_members:
            await update.message.reply_text(
                f"👋 Welcome {member.mention_html()}!\nEnjoy your stay 🚀",
                parse_mode="HTML"
            )

# ---------------- ? @username HANDLER ----------------
async def check_username(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Only trigger if message starts with "? @"
    text = update.message.text
    if text and text.startswith("? @"):
        username = text.replace("? @", "").strip()
        await update.message.reply_text(
            f"🔍 Checking @{username}...\n\n✅ Status: Not approved yet ❌"
        )

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
