from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import c
from config import AGENTS

async def notify_agents(context, case_id, name):
    for agent_id in AGENTS:
        try:
            await context.bot.send_message(agent_id, f"New ticket: {case_id} from {name}")
        except:
            pass

async def show_agent_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    agent_id = update.callback_query.from_user.id
    c.execute("SELECT case_id, user_id, status FROM cases WHERE status IN ('OPEN','IN_PROGRESS')")
    tickets = c.fetchall()
    if not tickets:
        await update.callback_query.message.reply_text("No open tickets.")
        return
    buttons = [
        [InlineKeyboardButton(f"{cid} - {status}", callback_data=f"case_{cid}")]
        for cid, user_id, status in tickets
    ]
    await update.callback_query.message.reply_text("Active Cases:", reply_markup=InlineKeyboardMarkup(buttons))

async def agent_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.message.reply_text("Agent action placeholder")
