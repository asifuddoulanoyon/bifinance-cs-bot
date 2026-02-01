from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import is_agent, conn, cursor

agent_cases = {}

async def show_cases(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if not is_agent(user_id):
        await update.message.reply_text("⚠️ You are not an agent.")
        return
    cursor.execute("SELECT case_id, status FROM cases WHERE agent_id=? OR status='OPEN'", (user_id,))
    rows = cursor.fetchall()
    buttons = [[InlineKeyboardButton(f"{r[0]} | {r[1]}", callback_data=r[0])] for r in rows]
    await update.message.reply_text("📂 Your Cases:", reply_markup=InlineKeyboardMarkup(buttons))

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    case_id = query.data
    agent_cases[query.from_user.id] = case_id
    await query.edit_message_text(f"✅ Case selected: {case_id}")

async def handle_agent_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id not in agent_cases:
        return
    case_id = agent_cases[user_id]
    if update.message.text:
        text = update.message.text
    else:
        text = "[MEDIA]"
    cursor.execute("UPDATE cases SET description=? WHERE case_id=?", (text, case_id))
    conn.commit()
    await update.message.reply_text(f"✅ Reply sent for {case_id}")

async def transfer_case(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("⚠️ Transfer feature coming soon.")

async def close_case(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id not in agent_cases:
        await update.message.reply_text("⚠️ No case selected.")
        return
    case_id = agent_cases[user_id]
    cursor.execute("UPDATE cases SET status='CLOSED' WHERE case_id=?", (case_id,))
    conn.commit()
    await update.message.reply_text(f"✅ Case {case_id} closed.")        cursor.execute("SELECT description, user_id FROM cases WHERE case_id=?", (case_id,))
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
