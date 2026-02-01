from telegram import Update
from telegram.ext import ContextTypes
from database import add_agent, remove_agent

async def add_agent(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /addagent <user_id>")
        return
    agent_id = int(context.args[0])
    add_agent(agent_id)
    await update.message.reply_text(f"✅ Agent {agent_id} added.")

async def remove_agent(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /removeagent <user_id>")
        return
    agent_id = int(context.args[0])
    remove_agent(agent_id)
    await update.message.reply_text(f"✅ Agent {agent_id} removed.")
