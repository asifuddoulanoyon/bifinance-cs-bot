import os

# Bot token and owner ID from environment
BOT_TOKEN = os.getenv("BOT_TOKEN")
OWNER_ID = int(os.getenv("OWNER_ID", 0))

# Database file
DB_FILE = "support.db"
