from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler, MessageHandler, filters, CallbackQueryHandler
from database import c, conn
from handlers.agent import show_agent_panel
from config import BOT_OWNER_ID, AGENTS
import random

NAME, UID, EMAIL, PROBLEM = range(4)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    buttons = [
        [InlineKeyboardButton("Create Ticket", callback_data="create_ticket")],
        [InlineKeyboardButton("My Tickets", callback_data="my_tickets")]
    ]
    user_id = update.message.from_user.id
    if user_id in AGENTS:
        buttons.append([InlineKeyboardButton("Agent Panel", callback_data="agent_panel")])
    markup = InlineKeyboardMarkup(buttons)
    await update.message.reply_text(
        "Welcome to Bifinance Customer Support. Use /help for instructions.",
        reply_markup=markup
    )

# The rest of user_button, name, uid, email, problem...
# (as in previous corrected version)
