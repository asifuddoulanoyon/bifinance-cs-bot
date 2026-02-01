from telegram import Update
from telegram.ext import ContextTypes
from database import cursor, conn
from datetime import datetime

# ----------------- Agent message handler -----------------
async def handle_agent_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    agent_id = update.message.from_user.id
    text = update.message.text
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

    # Find the case the agent wants to reply (simplified: last open case)
    cursor.execute("SELECT case_id, user_id FROM cases WHERE status='OPEN' ORDER BY created_at ASC LIMIT 1")
    row = cursor.fetchone()

    if not row:
        await update.message.reply_text("⚠️ No open tickets at the moment.")
        return

    case_id, user_id = row

    # Append agent reply
    cursor.execute(
        "UPDATE cases SET description = description || '\n\nAgent: ' || ?, updated_at=? WHERE case_id=?",
        (text, now, case_id)
    )
    conn.commit()

    await update.message.reply_text(f"✅ Your reply added to ticket {case_id}")

    # Notify user
    from telegram import Bot
    bot = Bot(token=os.getenv("BOT_TOKEN"))
    try:
        bot.send_message(chat_id=user_id, text=f"📩 Agent replied to your ticket {case_id}:\n{text}")
    except:
        pass
