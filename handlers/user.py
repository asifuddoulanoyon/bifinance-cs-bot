from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler, MessageHandler, filters, CallbackQueryHandler
from database import c, conn
from handlers.agent import notify_agents
from config import AGENTS
import random

NAME, UID, EMAIL, PROBLEM = range(4)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    buttons = [
        [InlineKeyboardButton("Create Ticket", callback_data="create_ticket")],
        [InlineKeyboardButton("My Tickets", callback_data="my_tickets")]
    ]
    if update.message.from_user.id in AGENTS:
        buttons.append([InlineKeyboardButton("Agent Panel", callback_data="agent_panel")])
    markup = InlineKeyboardMarkup(buttons)
    await update.message.reply_text("Welcome to Bifinance Customer Support. Use /help for instructions.", reply_markup=markup)

async def user_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    if query.data == "create_ticket":
        await query.message.reply_text("Enter your Name:")
        return NAME

    elif query.data == "my_tickets":
        c.execute("SELECT case_id, status FROM cases WHERE user_id=?", (user_id,))
        tickets = c.fetchall()
        if not tickets:
            await query.message.reply_text("No tickets found.")
            return
        buttons = [[InlineKeyboardButton(f"{cid} - {status}", callback_data=f"ticket_{cid}")] for cid, status in tickets]
        await query.message.reply_text("Your Tickets:", reply_markup=InlineKeyboardMarkup(buttons))

    elif query.data.startswith("ticket_"):
        case_id = query.data.split("_")[1]
        c.execute("SELECT problem, status FROM cases WHERE case_id=?", (case_id,))
        row = c.fetchone()
        if row:
            prob, status = row
            await query.message.reply_text(f"Case ID: {case_id}\nStatus: {status}\nProblem: {prob}")

async def name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["name"] = update.message.text
    await update.message.reply_text("Enter your UID (or type skip):")
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
    text = update.message.text or "Media sent"
    case_id = f"BF-{random.randint(100000,999999)}"
    user_id = update.message.from_user.id
    name_val = context.user_data["name"]
    uid_val = context.user_data["uid"]
    email_val = context.user_data["email"]

    c.execute(
        "INSERT INTO cases (case_id, user_id, name, uid, email, problem, status, conversation) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (case_id, user_id, name_val, uid_val, email_val, text, "OPEN", text)
    )
    conn.commit()

    await update.message.reply_text(f"Ticket created! Case ID: {case_id}")

    await notify_agents(context, case_id, name_val)

    return ConversationHandler.END
