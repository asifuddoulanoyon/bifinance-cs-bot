from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import create_case, get_user_active_case, append_message, close_case

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    active_case = get_user_active_case(user_id)
    if active_case:
        await update.message.reply_text(f"✅ You already have an active case: {active_case[1]}")
        return

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
    text = update.message.text
    user_id = update.effective_user.id

    if step == 'name':
        context.user_data['name'] = text
        context.user_data['step'] = 'uid'
        await update.message.reply_text("Your Bifinance UID (or type skip):")
    elif step == 'uid':
        context.user_data['uid'] = text if text.lower() != 'skip' else ''
        context.user_data['step'] = 'email'
        await update.message.reply_text("Your email:")
    elif step == 'email':
        context.user_data['email'] = text
        context.user_data['step'] = 'description'
        await update.message.reply_text("Describe your problem (text/photo/video/document):")
    elif step == 'description':
        context.user_data['description'] = text
        case_id = create_case(user_id, context.user_data['name'], context.user_data['uid'], context.user_data['email'], context.user_data['description'])
        await update.message.reply_text(f"✅ Your case has been submitted. Case ID: {case_id}")
        context.user_data['step'] = None        await update.message.reply_text("Describe your problem (text/photo/video/document):")
    elif step == 'description':
        context.user_data['description'] = text
        case_id = create_case(user_id, context.user_data['name'], context.user_data['uid'], context.user_data['email'], context.user_data['description'])
        await update.message.reply_text(f"✅ Your case has been submitted. Case ID: {case_id}")
        context.user_data['step'] = None        await update.message.reply_text("Describe your problem (text/photo/video/document):")
    elif step == 'description':
        context.user_data['description'] = text
        case_id = create_case(user_id, context.user_data['name'], context.user_data['uid'], context.user_data['email'], context.user_data['description'])
        await update.message.reply_text(f"✅ Your case has been submitted. Case ID: {case_id}")
        context.user_data['step'] = None        await update.message.reply_text("Describe your problem (text/photo/video/document):")
    elif step == 'description':
        context.user_data['description'] = text
        # Create case
        case_id = create_case(user_id, context.user_data['name'], context.user_data['uid'], context.user_data['email'], context.user_data['description'])
        await update.message.reply_text(f"✅ Your case has been submitted. Case ID: {case_id}")
        context.user_data['step'] = None
