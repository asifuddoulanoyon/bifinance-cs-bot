from telegram.ext import CallbackQueryHandler, CommandHandler

from handlers.agent import agent_panel, agent_button
from config import AGENTS, BOT_OWNER_ID

# Admin commands
async def add_agent(update, context):
    if update.effective_user.id != BOT_OWNER_ID:
        await update.message.reply_text("Not authorized")
        return
    if not context.args:
        await update.message.reply_text("Usage: /addagent <user_id>")
        return
    AGENTS.append(int(context.args[0]))
    await update.message.reply_text(f"Added agent {context.args[0]}")

async def remove_agent(update, context):
    if update.effective_user.id != BOT_OWNER_ID:
        await update.message.reply_text("Not authorized")
        return
    if not context.args:
        await update.message.reply_text("Usage: /removeagent <user_id>")
        return
    AGENTS.remove(int(context.args[0]))
    await update.message.reply_text(f"Removed agent {context.args[0]}")

app.add_handler(CommandHandler("addagent", add_agent))
app.add_handler(CommandHandler("removeagent", remove_agent))

# Agent panel
app.add_handler(CommandHandler("agent", agent_panel))
app.add_handler(CallbackQueryHandler(agent_button, pattern="^(take_|reply_|close_)"))
