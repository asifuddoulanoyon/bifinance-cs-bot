from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import get_active_cases_for_agent, assign_case, append_message

async def list_cases(update: Update, context: ContextTypes.DEFAULT_TYPE):
    agent_id = update.effective_user.id
    cases = get_active_cases_for_agent(agent_id)
    if not cases:
        await update.message.reply_text("📂 No active cases assigned to you.")
        return
    buttons = []
    for c in cases:
        buttons.append([InlineKeyboardButton(f"{c[1]} | User: {c[2]}", callback_data=f"case_{c[1]}")])
    markup = InlineKeyboardMarkup(buttons)
    await update.message.reply_text("📂 Your active cases:", reply_markup=markup)

async def reply_case(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 2:
        await update.message.reply_text("Usage: /reply <case_id> <message>")
        return
    case_id = context.args[0]
    text = " ".join(context.args[1:])
    append_message(case_id, f"Agent {update.effective_user.first_name}", text)
    await update.message.reply_text(f"✉️ Reply sent to {case_id}")
