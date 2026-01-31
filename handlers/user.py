from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler, MessageHandler, filters
from database import create_case, append_message, get_user_active_case
from handlers.agent import notify_agents

NAME, UID, EMAIL, PROBLEM = range(4)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Welcome to Bifinance Customer Support!\nUse /help for instructions."
    )

async def user_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    case_id = get_user_active_case(user_id)
    if not case_id:
        await update.message.reply_text("No active case. Use /start to create a ticket.")
        return

    text = update.message.text or "Media sent"
    append_message(case_id, "User", text)

    from handlers.agent import notify_assigned_agent
    await notify_assigned_agent(context, case_id)
    await update.message.reply_text("Your message has been sent to the agent.")

async def create_ticket_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Enter your Name:")
    return NAME

async def name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["name"] = update.message.text
    await update.message.reply_text("Enter your UID (or skip):")
    return UID

async def uid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    context.user_data["uid"] = None if text.lower() == "skip" else text
    await update.message.reply_text("Enter your Email:")
    return EMAIL

async def email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if "@" not in text:
        await update.message.reply_text("Invalid email. Try again:")
        return EMAIL
    context.user_data["email"] = text
    await update.message.reply_text("Describe your problem:")
    return PROBLEM

async def problem(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = update.message.from_user.id
    name = context.user_data["name"]
    uid = context.user_data["uid"]
    email = context.user_data["email"]

    case_id = create_case(user_id, name, uid, email, text)
    await update.message.reply_text(f"Ticket created! Case ID: {case_id}")

    # Notify all agents
    await notify_agents(context, case_id, name)
    return ConversationHandler.END
