from telegram import Update
from telegram.ext import ContextTypes

async def list_cases(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # TODO: Fetch cases from DB and show buttons
    await update.message.reply_text("📂 List of active cases (placeholder)")

async def reply_case(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✉️ Reply sent (placeholder)")
