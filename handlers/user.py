from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Welcome to Bifinance Customer Support\n"
        "This is the only official support channel.\n"
        "Please answer the questions to create a support ticket.\n"
        "Use /help for instructions."
    )
    context.user_data['step'] = 'name'
    await update.message.reply_text("What is your name?")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    step = context.user_data.get('step')
    if step == 'name':
        context.user_data['name'] = update.message.text
        context.user_data['step'] = 'uid'
        await update.message.reply_text("Your Bifinance UID (or type skip):")
    elif step == 'uid':
        context.user_data['uid'] = update.message.text if update.message.text.lower() != 'skip' else ''
        context.user_data['step'] = 'email'
        await update.message.reply_text("Your email:")
    elif step == 'email':
        context.user_data['email'] = update.message.text
        context.user_data['step'] = 'description'
        await update.message.reply_text("Describe your problem (text/photo/video/document):")
    elif step == 'description':
        context.user_data['description'] = update.message.text
        # TODO: Save case to database and notify agents
        await update.message.reply_text("✅ Your case has been submitted. An agent will contact you soon.")
        context.user_data['step'] = None
