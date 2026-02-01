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
    for member in update.message.new_chat_members:
        await update.message.reply_text(
            f"👋 Welcome {member.mention_html()}!\nEnjoy your stay 🚀",
            parse_mode="HTML"
        )

# ---------------- ? @username HANDLER ----------------
async def check_username(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()

    if text.startswith("? @"):
        username = text.replace("? @", "").strip()

        await update.message.reply_text(
            f"🔍 Checking @{username}...\n\n✅ Status: Not approved yet ❌"
        )

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
