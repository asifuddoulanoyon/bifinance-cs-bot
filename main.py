import logging
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)
from config import BOT_TOKEN, ADMIN_IDS, AGENT_IDS

logging.basicConfig(level=logging.INFO)

# In-memory storage (SAFE, SIMPLE, WORKS)
tickets = {}  # user_id -> agent_id

# ---------------- START ----------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if user_id in ADMIN_IDS:
        await update.message.reply_text(
            "👑 Admin mode\n"
            "You will receive all new tickets.\n"
            "Reply to any user to chat."
        )
        return

    if user_id in AGENT_IDS:
        await update.message.reply_text(
            "🧑‍💼 Agent mode\n"
            "You will receive assigned tickets."
        )
        return

    await update.message.reply_text(
        "🎫 Welcome to Support\n\n"
        "Send your message to create a ticket."
    )

# ---------------- USER MESSAGE ----------------
async def user_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text

    # Assign first agent/admin automatically
    agent_id = AGENT_IDS[0]
    tickets[user_id] = agent_id

    await update.message.reply_text(
        "✅ Ticket created.\n"
        "An agent will reply soon."
    )

    await context.bot.send_message(
        chat_id=agent_id,
        text=(
            "📩 New Ticket\n\n"
            f"User ID: {user_id}\n"
            f"Message:\n{text}\n\n"
            "Reply to this message to answer."
        )
    )

# ---------------- AGENT / ADMIN REPLY ----------------
async def agent_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        return

    sender_id = update.effective_user.id
    if sender_id not in ADMIN_IDS and sender_id not in AGENT_IDS:
        return

    original = update.message.reply_to_message.text
    lines = original.splitlines()

    user_id = None
    for line in lines:
        if line.startswith("User ID:"):
            user_id = int(line.replace("User ID:", "").strip())

    if not user_id:
        await update.message.reply_text("❌ Cannot find user.")
        return

    await context.bot.send_message(
        chat_id=user_id,
        text=f"💬 Support:\n{update.message.text}"
    )

    await update.message.reply_text("✅ Sent to user.")

# ---------------- ROUTER ----------------
async def router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if user_id in ADMIN_IDS or user_id in AGENT_IDS:
        await agent_reply(update, context)
    else:
        await user_message(update, context)

# ---------------- MAIN ----------------
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, router))

    print("🤖 Support bot running")
    app.run_polling()

if __name__ == "__main__":
    main()        update = Update.de_json(request.get_json(force=True), app.bot)
        app.update_queue.put(update)
        return "ok"

    # Start Flask app
    flask_app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
