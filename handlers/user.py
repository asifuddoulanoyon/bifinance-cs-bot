from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import cursor, conn
from datetime import datetime

# ----------------- User message handler -----------------
async def handle_user_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    text = update.message.text
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

    # Check if user exists
    cursor.execute("SELECT active_case_id FROM users WHERE user_id=?", (user_id,))
    row = cursor.fetchone()

    if row:
        active_case_id = row[0]
    else:
        # New user, create entry
        cursor.execute("INSERT OR IGNORE INTO users(user_id) VALUES(?)", (user_id,))
        conn.commit()
        active_case_id = None

    # If no active case, create one
    if not active_case_id:
        cursor.execute("SELECT COUNT(*) FROM cases")
        count = cursor.fetchone()[0] + 1
        case_id = f"BF-{datetime.utcnow().year}-{count:06d}"

        cursor.execute(
            "INSERT INTO cases(case_id, user_id, description, status, created_at, updated_at) VALUES(?,?,?,?,?,?)",
            (case_id, user_id, text, "OPEN", now, now)
        )
        cursor.execute("UPDATE users SET active_case_id=? WHERE user_id=?", (case_id, user_id))
        conn.commit()
        active_case_id = case_id

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
