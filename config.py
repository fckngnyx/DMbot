import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TOKEN")
CLIENT_BOT_TOKEN = os.getenv("CLIENT_BOT_TOKEN")
ADMIN_IDS = os.getenv("ADMIN_IDS", "").split(",")
