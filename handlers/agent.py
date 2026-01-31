from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes
from database import c, assign_agent, append_message, close_case
from config import AGENTS

async def notify_agents(context, case_id, user_name):
    for agent_id in AGENTS:
        try:
            await context.bot.send_message(agent_id, f"📩 New Ticket {case_id} from {user_name}")
        except:
            pass

async def notify_assigned_agent(context, case_id):
    c.execute("SELECT assigned_agent FROM cases WHERE case_id=?", (case_id,))
    row = c.fetchone()
    if row and row[0]:
        agent_id = row[0]
        await context.bot.send_message(agent_id, f"🆕 New message in Case {case_id}")

async def agent_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    agent_id = update.effective_user.id
    c.execute("SELECT case_id, user_id, status FROM cases WHERE status IN ('OPEN','IN_PROGRESS')")
    tickets = c.fetchall()
    if not tickets:
        await update.message.reply_text("No open tickets.")
        return
    buttons = [
        [InlineKeyboardButton(f"{cid} - {status}", callback_data=f"take_{cid}")]
        for cid, user_id, status in tickets
    ]
    await update.message.reply_text("Active Cases:", reply_markup=InlineKeyboardMarkup(buttons))

async def agent_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    agent_id = query.from_user.id
    await query.answer()

    if query.data.startswith("take_"):
        case_id = query.data.split("_")[1]
        assign_agent(case_id, agent_id)
        await query.message.reply_text(f"You have taken Case {case_id}")

    elif query.data.startswith("reply_"):
        # Here we would open a mini-FSM for agent reply
        await query
