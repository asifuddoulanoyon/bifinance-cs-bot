from telegram import Update
from telegram.ext import ContextTypes
from database import add_user, create_case
from telegram import ReplyKeyboardMarkup

user_data = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    await update.message.reply_text(
        "👋 Welcome to Bifinance Customer Support!\nPlease answer the following questions to create a support ticket."
    )
    user_data[user_id] = {"step": 1}
    await update.message.reply_text("1️⃣ What is your name?")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "/start - Create new ticket\n/help - Show this manual\nReply to open ticket - Continue conversation\n/close - Close ticket"
    )

async def handle_user_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    text = update.message.text
    if user_id not in user_data:
        await update.message.reply_text("⚠️ Use /start to create a new ticket.")
        return

    step = user_data[user_id]["step"]

    # Step 1: Name
    if step == 1:
        user_data[user_id]["name"] = text
        user_data[user_id]["step"] = 2
        await update.message.reply_text("2️⃣ Your Bifinance UID? (or type skip)")
        return

    # Step 2: UID
    if step == 2:
        user_data[user_id]["uid"] = None if text.lower() == "skip" else text
        user_data[user_id]["step"] = 3
        await update.message.reply_text("3️⃣ Your Email address?")
        return

    # Step 3: Email (basic validation)
    if step == 3:
        if "@" not in text or "." not in text:
            await update.message.reply_text("⚠️ Invalid email. Try again.")
            return
        user_data[user_id]["email"] = text
        user_data[user_id]["step"] = 4
        await update.message.reply_text("4️⃣ Describe your problem:")
        return

    # Step 4: Problem description
    if step == 4:
        name = user_data[user_id]["name"]
        uid = user_data[user_id]["uid"]
        email = user_data[user_id]["email"]
        add_user(user_id, name, uid, email)
        case_id = create_case(user_id, text)
        user_data[user_id]["active_case_id"] = case_id
        user_data[user_id]["step"] = None
        await update.message.reply_text(f"✅ Ticket created! Case ID: {case_id}")
        # Notify user
        await update.message.reply_text(f"✅ Ticket created: {active_case_id}\nOur agents will reply soon!")

    else:
        # Append message to case
        cursor.execute(
            "UPDATE cases SET description = description || '\n\nUser: ' || ?, updated_at=? WHERE case_id=?",
            (text, now, active_case_id)
        )
        conn.commit()
        await update.message.reply_text(f"✅ Your message has been added to ticket {active_case_id}")
