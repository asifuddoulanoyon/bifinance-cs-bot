from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler
from database import cursor, conn
from datetime import datetime
import os
from telegram import Bot

bot = Bot(token=os.getenv("BOT_TOKEN"))

# ----------------- Show active cases to agent -----------------
async def show_cases(update: Update, context: ContextTypes.DEFAULT_TYPE):
    agent_id = update.message.from_user.id

    cursor.execute("SELECT case_id, status FROM cases WHERE agent_id=?", (agent_id,))
    rows = cursor.fetchall()

    if not rows:
        await update.message.reply_text("⚠️ You have no assigned cases.")
        return

    buttons = [
        [InlineKeyboardButton(f"{case_id} ({status})", callback_data=f"case_{case_id}")]
        for case_id, status in rows
    ]
    markup = InlineKeyboardMarkup(buttons)
    await update.message.reply_text("📂 Your active cases:", reply_markup=markup)


# ----------------- Handle agent button clicks -----------------
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    agent_id = query.from_user.id

    if query.data.startswith("case_"):
        case_id = query.data.split("_")[1]
        cursor.execute("SELECT description, user_id FROM cases WHERE case_id=?", (case_id,))
        row = cursor.fetchone()
        if not row:
            await query.edit_message_text("⚠️ Case not found.")
            return

        description, user_id = row
        await query.edit_message_text(f"📝 Case {case_id}:\n{description}\n\nYou can reply now.")


# ----------------- Agent replies to user -----------------
async def handle_agent_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    agent_id = update.message.from_user.id
    text = update.message.text
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

    # For simplicity, reply to last assigned open case
    cursor.execute(
        "SELECT case_id, user_id FROM cases WHERE agent_id=? AND status='OPEN' ORDER BY created_at ASC LIMIT 1",
        (agent_id,)
    )
    row = cursor.fetchone()
    if not row:
        await update.message.reply_text("⚠️ You have no open tickets.")
        return

    case_id, user_id = row

    cursor.execute(
        "UPDATE cases SET description = description || '\n\nAgent: ' || ?, updated_at=? WHERE case_id=?",
        (text, now, case_id)
    )
    conn.commit()
    await update.message.reply_text(f"✅ Replied to ticket {case_id}")

    # Notify user
    try:
        await bot.send_message(chat_id=user_id, text=f"📩 Agent replied to your ticket {case_id}:\n{text}")
    except:
        pass


# ----------------- Transfer case -----------------
async def transfer_case(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 2:
        await update.message.reply_text("Usage: /transfer <case_id> <new_agent_id>")
        return

    case_id = context.args[0]
    new_agent_id = int(context.args[1])

    cursor.execute("UPDATE cases SET agent_id=? WHERE case_id=?", (new_agent_id, case_id))
    conn.commit()
    await update.message.reply_text(f"✅ Case {case_id} transferred to {new_agent_id}")

    # Notify new agent
    try:
        await bot.send_message(chat_id=new_agent_id, text=f"📂 You received a new case: {case_id}")
    except:
        pass


# ----------------- Close case -----------------
async def close_case(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /close <case_id>")
        return

    case_id = context.args[0]
    cursor.execute("SELECT user_id FROM cases WHERE case_id=?", (case_id,))
    row = cursor.fetchone()
    if not row:
        await update.message.reply_text("⚠️ Case not found.")
        return

    user_id = row[0]
    cursor.execute("UPDATE cases SET status='CLOSED' WHERE case_id=?", (case_id,))
    cursor.execute("UPDATE users SET active_case_id=NULL WHERE user_id=?", (user_id,))
    conn.commit()

    await update.message.reply_text(f"✅ Case {case_id} closed")

    # Notify user
    try:
        await bot.send_message(chat_id=user_id, text=f"✅ Your ticket {case_id} has been closed. Please rate your agent!")
    except:
        pass        pass
