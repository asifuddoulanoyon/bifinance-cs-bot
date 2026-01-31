import os

BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN is missing")

# PUT YOUR REAL TELEGRAM ID HERE
ADMIN_IDS = [1675295056]
AGENT_IDS = [1675295056]  # you can be agent + admin
