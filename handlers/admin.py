from telegram import Update
from telegram.ext import ContextTypes
from config import OWNER_ID

async def add_agent(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        return
    await update.message.reply_text("✅ Agent added (admin placeholder)")

async def remove_agent(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        return
    await update.message.reply_text("✅ Agent removed (admin placeholder)")
