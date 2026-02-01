from telegram import Update
from telegram.ext import ContextTypes
from database import cursor, conn

async def add_agent(update: Update, context: ContextTypes.DEFAULT_TYPE):
    owner_id = int(os.getenv("OWNER_ID"))
    if update.message.from_user.id != owner_id:
        await update.message.reply_text("❌ You are not the owner.")
        return

    if not context.args:
        await update.message.reply_text("Usage: /addagent <agent_telegram_id>")
        return

    agent_id = int(context.args[0])
    cursor.execute("INSERT OR IGNORE INTO agents(agent_id) VALUES(?)", (agent_id,))
    conn.commit()
    await update.message.reply_text(f"✅ Agent {agent_id} added.")

async def remove_agent(update: Update, context: ContextTypes.DEFAULT_TYPE):
    owner_id = int(os.getenv("OWNER_ID"))
    if update.message.from_user.id != owner_id:
        await update.message.reply_text("❌ You are not the owner.")
        return

    if not context.args:
        await update.message.reply_text("Usage: /removeagent <agent_telegram_id>")
        return

    agent_id = int(context.args[0])
    cursor.execute("DELETE FROM agents WHERE agent_id=?", (agent_id,))
    conn.commit()
    await update.message.reply_text(f"✅ Agent {agent_id} removed.")
