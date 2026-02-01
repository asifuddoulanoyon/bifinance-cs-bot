from telegram import Update
from telegram.ext import ContextTypes
import sqlite3

DB_NAME = "support.db"

async def list_cases(update: Update, context: ContextTypes.DEFAULT_TYPE):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT case_id, status FROM cases WHERE status IN ('OPEN', 'IN_PROGRESS')")
    rows = c.fetchall()
    if not rows:
        await update.message.reply_text("No active cases.")
    else:
        message = "Active Cases:\n" + "\n".join([f"• {r[0]} - {r[1]}" for r in rows])
        await update.message.reply_text(message)
    conn.close()

async def reply_case(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 2:
        await update.message.reply_text("Usage: /reply <CASE_ID> <message>")
        return
    case_id = context.args[0]
    reply_text = " ".join(context.args[1:])
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT history FROM cases WHERE case_id=?", (case_id,))
    row = c.fetchone()
    if not row:
        await update.message.reply_text("Case not found.")
    else:
        history = row[0] + f"\nAgent: {reply_text}"
        c.execute("UPDATE cases SET history=?, updated_at=CURRENT_TIMESTAMP WHERE case_id=?",
                  (history, case_id))
        conn.commit()
        await update.message.reply_text(f"✅ Replied to {case_id}.")
    conn.close()
