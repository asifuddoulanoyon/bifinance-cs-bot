from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from database import c, assign_agent, append_message

AGENTS_LIST = []

async def notify_agents(context, case_id, name):
    from config import AGENTS
    for agent_id in AGENTS:
        try:
            await context.bot.send_message(agent_id, f"📩 New Ticket {case_id} from {name}")
        except:
            pass

async def notify_assigned_agent(context, case_id):
    c.execute("SELECT assigned_agent FROM cases WHERE case_id=?", (case_id,))
    row = c.fetchone()
    if row and row[0]:
        agent_id = row[0]
        await context.bot.send_message(agent_id, f"🆕 New message in Case {case_id}")
