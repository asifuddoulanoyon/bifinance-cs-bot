from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from database import c, conn
from config import BOT_OWNER_ID, AGENTS

async def show_agent_panel(update, context):
    user_id = update.callback_query.from_user.id if update.callback_query else update.message.from_user.id
    if user_id not in AGENTS:
        await (update.message.reply_text("❌ Not authorized.") if update.message else update.callback_query.message.reply_text("❌ Not authorized."))
        return

    c.execute("SELECT case_id, status FROM cases WHERE assigned_agent=? OR assigned_agent IS NULL", (user_id,))
    cases = c.fetchall()
    buttons = [[InlineKeyboardButton(f"{c_id} - {status}", callback_data=f"case_{c_id}")] for c_id, status in cases]
    markup = InlineKeyboardMarkup(buttons) if buttons else None
    await (update.message.reply_text("📂 Your Tickets:", reply_markup=markup) if update.message else update.callback_query.message.reply_text("📂 Your Tickets:", reply_markup=markup))

async def agent_button(update, context):
    query = update.callback_query
    await query.answer()
    data = query.data
    if data.startswith("case_"):
        case_id = data.split("_")[1]
        context.user_data["current_case"] = case_id
        c.execute("SELECT problem, status FROM cases WHERE case_id=?", (case_id,))
        prob, status = c.fetchone()
        keyboard = [[InlineKeyboardButton("Transfer", callback_data="transfer"), InlineKeyboardButton("Close", callback_data="close")]]
        await query.edit_message_text(f"📝 {case_id}\nStatus: {status}\nProblem: {prob}", reply_markup=InlineKeyboardMarkup(keyboard))
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
        c.execute("SELECT user_id FROM cases WHERE case_id=?", (case_id,))
        user_id = c.fetchone()[0]
        keyboard = [[InlineKeyboardButton(str(i), callback_data=f"rate_{case_id}_{i}")] for i in range(1,6)]
        try:
            await context.bot.send_message(user_id, "✅ Your ticket is closed! Please rate:", reply_markup=InlineKeyboardMarkup(keyboard))
        except: pass
        await query.edit_message_text(f"✅ Ticket {case_id} closed")
