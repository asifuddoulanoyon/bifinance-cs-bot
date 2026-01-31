from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler
from database import c, conn
from config import AGENTS

# Show agent panel
async def show_agent_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.callback_query.from_user.id
    if user_id not in AGENTS:
        await update.callback_query.message.reply_text("❌ Not authorized")
        return
    # Show all assigned cases
    c.execute("SELECT case_id, status FROM cases WHERE assigned_agent=?", (user_id,))
    cases = c.fetchall()
    buttons = [[InlineKeyboardButton(f"{c_id} - {status}", callback_data=f"case_{c_id}")] for c_id, status in cases]
    if not buttons:
        await update.callback_query.message.reply_text("No active cases assigned.")
        return
    await update.callback_query.message.reply_text("📂 Your Active Cases:", reply_markup=InlineKeyboardMarkup(buttons))

# Handle agent buttons
async def agent_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    if user_id not in AGENTS:
        await query.message.reply_text("❌ Not authorized")
        return
    # Example: open case, transfer, close logic (same as Replit)
    # Implement your exact Replit logic here
