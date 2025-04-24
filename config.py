import os

from dotenv import load_dotenv
load_dotenv()

# Токен для админского бота
ADMIN_BOT_TOKEN = os.getenv("ADMIN_BOT_TOKEN")

# Токен для клиентского бота
CLIENT_BOT_TOKEN = os.getenv("CLIENT_BOT_TOKEN")

ADMIN_IDS = os.getenv("ADMIN_IDS", "").split(",")
