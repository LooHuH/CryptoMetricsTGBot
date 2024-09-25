import os
from dotenv import load_dotenv

load_dotenv()

TG_TOKEN = os.getenv("BOT_TOKEN")
API_TOKEN = os.getenv("API_TOKEN")

base_dir = os.path.dirname(os.path.abspath(__file__))
