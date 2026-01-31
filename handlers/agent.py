from telegram import Update
from telegram.ext import ContextTypes

async def show_agent_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.message.reply_text("Agent panel placeholder. You can implement multi-case logic here.")

async def agent_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.message.reply_text("Agent button clicked")
