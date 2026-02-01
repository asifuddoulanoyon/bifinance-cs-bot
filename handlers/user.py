from telegram import Update
from telegram.ext import ContextTypes
import sqlite3

DB_NAME = "support.db"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Welcome to Bifinance Customer Support!\n"
        "Use /help for instructions.\n"
        "Please provide your name to start a ticket."
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    telegram_id = update.message.from_user.id
    text = update.message.text

    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT active_case_id FROM users WHERE telegram_id=?", (telegram_id,))
    row = c.fetchone()

    if not row or not row[0]:
        # No active case, create new
        case_id = f"BF-{telegram_id}-{int(update.message.message_id)}"
        c.execute("INSERT OR REPLACE INTO users (telegram_id, name, active_case_id) VALUES (?, ?, ?)",
                  (telegram_id, update.message.from_user.full_name, case_id))
        c.execute("INSERT INTO cases (case_id, user_id, description, status, history) VALUES (?, ?, ?, ?, ?)",
                  (case_id, telegram_id, text, "OPEN", text))
        conn.commit()
        await update.message.reply_text(f"✅ Ticket created. Case ID: {case_id}")
    else:
        # Append to active case
        case_id = row[0]
        c.execute("SELECT history FROM cases WHERE case_id=?", (case_id,))
        history = c.fetchone()[0]
        history += f"\nUser: {text}"
        c.execute("UPDATE cases SET history=?, updated_at=CURRENT_TIMESTAMP WHERE case_id=?",
                  (history, case_id))
        conn.commit()
        await update.message.reply_text("✅ Your message added to the active case.")
    conn.close()
