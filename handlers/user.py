async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Create Ticket", callback_data="create_ticket")],
        [InlineKeyboardButton("My Tickets", callback_data="my_tickets")]
    ]
    markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("👋 Welcome! What do you want to do?", reply_markup=markup)

async def user_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "create_ticket":
        await query.message.reply_text("Enter your *Name*:", parse_mode="Markdown")
        return NAME
    elif query.data == "my_tickets":
        user_id = query.from_user.id
        c.execute("SELECT case_id, status FROM cases WHERE user_id=?", (user_id,))
        tickets = c.fetchall()
        if not tickets:
            await query.message.reply_text("❌ You have no tickets yet.")
            return
        buttons = [[InlineKeyboardButton(f"{c_id} - {status}", callback_data=f"ticket_{c_id}")] for c_id, status in tickets]
        await query.message.reply_text("📂 Your Tickets:", reply_markup=InlineKeyboardMarkup(buttons))
    elif query.data.startswith("ticket_"):
        case_id = query.data.split("_")[1]
        c.execute("SELECT problem, status FROM cases WHERE case_id=?", (case_id,))
        prob, status = c.fetchone()
        text = f"📝 {case_id}\nStatus: {status}\nProblem: {prob}"
        if status == "CLOSED":
            keyboard = [[InlineKeyboardButton(str(i), callback_data=f"rate_{case_id}_{i}")] for i in range(1,6)]
            await query.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
        else:
            await query.message.reply_text(text)
