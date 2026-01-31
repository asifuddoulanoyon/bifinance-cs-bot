from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import c, conn
from config import BOT_OWNER_ID, AGENTS

async def start_agent(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id != BOT_OWNER_ID and user_id not in AGENTS:
        await update.message.reply_text("❌ You are not authorized as agent.")
        return
    await show_agent_panel(update, context)

async def show_agent_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    agent_id = update.message.from_user.id
    c.execute("SELECT case_id, status FROM cases WHERE assigned_agent=? OR assigned_agent IS NULL", (agent_id,))
    cases = c.fetchall()
    buttons = [[InlineKeyboardButton(f"{c_id} - {status}", callback_data=f"case_{c_id}")] for c_id, status in cases]
    markup = InlineKeyboardMarkup(buttons) if buttons else None
    await update.message.reply_text("📂 Your Tickets:", reply_markup=markup or None)

async def agent_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    if data.startswith("case_"):
        case_id = data.split("_")[1]
        context.user_data["current_case"] = case_id
        c.execute("SELECT problem, status FROM cases WHERE case_id=?", (case_id,))
        prob, status = c.fetchone()
        keyboard = [
            [InlineKeyboardButton("Transfer", callback_data="transfer"), InlineKeyboardButton("Close", callback_data="close")]
        ]
        markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(f"📝 {case_id}\nStatus: {status}\nProblem: {prob}", reply_markup=markup)
    elif data == "transfer":
        keyboard = [[InlineKeyboardButton(str(aid), callback_data=f"transfer_{aid}")] for aid in AGENTS]
        await query.edit_message_text("Select agent to transfer:", reply_markup=InlineKeyboardMarkup(keyboard))
    elif data.startswith("transfer_"):
        new_agent = int(data.split("_")[1])
        case_id = context.user_data["current_case"]
        c.execute("UPDATE cases SET assigned_agent=? WHERE case_id=?", (new_agent, case_id))
        conn.commit()
        await query.edit_message_text(f"✅ Ticket {case_id} transferred to agent {new_agent}")
    elif data == "close":
        case_id = context.user_data["current_case"]
        c.execute("UPDATE cases SET status='CLOSED' WHERE case_id=?", (case_id,))
        conn.commit()
        # Notify user
        c.execute("SELECT user_id FROM cases WHERE case_id=?", (case_id,))
        user_id = c.fetchone()[0]
        keyboard = [[InlineKeyboardButton(str(i), callback_data=f"rate_{case_id}_{i}")] for i in range(1,6)]
        await context.bot.send_message(user_id, "✅ Your ticket is closed! Please rate the agent:", reply_markup=InlineKeyboardMarkup(keyboard))
        await query.edit_message_text(f"✅ Ticket {case_id} closed")

async def agent_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if "current_case" not in context.user_data:
        await update.message.reply_text("Select a ticket first.")
        return
    case_id = context.user_data["current_case"]
    text = update.message.text or "Media sent"
    c.execute("UPDATE cases SET conversation = conversation || ? WHERE case_id=?", (f"\nAgent: {text}", case_id))
    conn.commit()
    c.execute("SELECT user_id FROM cases WHERE case_id=?", (case_id,))
    user_id = c.fetchone()[0]
    try:
        await context.bot.send_message(user_id, f"💬 Agent replied:\n{text}")
    except: pass
    await update.message.reply_text("Message sent to user.")
