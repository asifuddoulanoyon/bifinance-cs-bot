from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes, ConversationHandler, MessageHandler, filters
from database import c, assign_agent, append_message, close_case

# FSM states for agent actions
AGENT_REPLY, AGENT_RATE = range(2)

# Show bottom buttons for multi-case handling
def agent_case_buttons(agent_id):
    c.execute("SELECT case_id, status FROM cases WHERE assigned_agent=?", (agent_id,))
    cases = c.fetchall()
    buttons = []
    for cid, status in cases:
        buttons.append([InlineKeyboardButton(f"{cid} - {status}", callback_data=f"switch_{cid}")])
    return InlineKeyboardMarkup(buttons) if buttons else None

async def agent_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    agent_id = query.from_user.id
    await query.answer()
    data = query.data

    if data.startswith("take_"):
        case_id = data.split("_")[1]
        assign_agent(case_id, agent_id)
        await query.message.reply_text(f"You have taken Case {case_id}")
        await send_agent_case_panel(query, agent_id, case_id)

    elif data.startswith("switch_"):
        case_id = data.split("_")[1]
        await send_agent_case_panel(query, agent_id, case_id)

    elif data.startswith("reply_"):
        case_id = data.split("_")[1]
        context.user_data["reply_case_id"] = case_id
        await query.message.reply_text(f"Send your reply for Case {case_id}:")
        return AGENT_REPLY

    elif data.startswith("close_"):
        case_id = data.split("_")[1]
        close_case(case_id)
        await query.message.reply_text(f"Case {case_id} closed!")
        # Ask user to rate agent
        c.execute("SELECT user_id FROM cases WHERE case_id=?", (case_id,))
        row = c.fetchone()
        if row:
            user_id = row[0]
            buttons = [
                [InlineKeyboardButton("⭐1", callback_data=f"rate_{case_id}_1"),
                 InlineKeyboardButton("⭐2", callback_data=f"rate_{case_id}_2"),
                 InlineKeyboardButton("⭐3", callback_data=f"rate_{case_id}_3"),
                 InlineKeyboardButton("⭐4", callback_data=f"rate_{case_id}_4"),
                 InlineKeyboardButton("⭐5", callback_data=f"rate_{case_id}_5")]
            ]
            await context.bot.send_message(user_id, f"Case {case_id} closed. Please rate your agent:", reply_markup=InlineKeyboardMarkup(buttons))

    elif data.startswith("rate_"):
        parts = data.split("_")
        case_id = parts[1]
        rating = int(parts[2])
        c.execute("UPDATE cases SET user_rating=? WHERE case_id=?", (rating, case_id))
        await query.message.reply_text(f"Thanks for rating! ⭐{rating}")

    elif data.startswith("transfer_"):
        parts = data.split("_")
        case_id = parts[1]
        target_agent = int(parts[2])
        assign_agent(case_id, target_agent)
        await query.message.reply_text(f"Case {case_id} transferred to agent {target_agent}")

async def send_agent_case_panel(query, agent_id, case_id):
    buttons = [
        [InlineKeyboardButton("Reply", callback_data=f"reply_{case_id}")],
        [InlineKeyboardButton("Close", callback_data=f"close_{case_id}")]
    ]
    # Transfer button: list all other agents
    from config import AGENTS
    transfer_buttons = []
    for a_id in AGENTS:
        if a_id != agent_id:
            transfer_buttons.append(InlineKeyboardButton(f"Transfer to {a_id}", callback_data=f"transfer_{case_id}_{a_id}"))
    if transfer_buttons:
        buttons.append(transfer_buttons)
    await query.message.reply_text(f"Case Panel for {case_id}:", reply_markup=InlineKeyboardMarkup(buttons))

# FSM for agent reply
async def agent_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    agent_id = update.effective_user.id
    text = update.message.text or "Media sent"
    case_id = context.user_data.get("reply_case_id")
    if not case_id:
        await update.message.reply_text("No case selected.")
        return ConversationHandler.END
    append_message(case_id, f"Agent {agent_id}", text)
    # Notify user
    c.execute("SELECT user_id FROM cases WHERE case_id=?", (case_id,))
    row = c.fetchone()
    if row:
        user_id = row[0]
        await update.message.bot.send_message(user_id, f"🛡️ **Bifinance Support**
