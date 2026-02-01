from telegram import Update
from telegram.ext import ContextTypes
import sqlite3

DB_NAME = "support.db"

async def add_agent(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 2:
        await update.message.reply_text("Usage: /addagent <Telegram_ID> <Name>")
        return
    telegram_id = int(context.args[0])
    name = context.args[1]
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO agents (telegram_id, name) VALUES (?, ?)", (telegram_id, name))
    conn.commit()
    conn.close()
    await update.message.reply_text(f"✅ Agent {name} added.")

async def remove_agent(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 1:
        await update.message.reply_text("Usage: /removeagent <Telegram_ID>")
        return
    telegram_id = int(context.args[0])
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("DELETE FROM agents WHERE telegram_id=?", (telegram_id,))
    conn.commit()
    conn.close()
    await update.message.reply_text(f"✅ Agent removed.")
