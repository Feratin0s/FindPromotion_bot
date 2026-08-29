import json
import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

def load_secrets():
    return {
        "bot_token": os.getenv("bot_token"),
        "api_id": os.getenv("api_id"),
        "api_hash": os.getenv("api_hash"),
        "phone_number": os.getenv("phone_number"),
        "destiny": os.getenv("destiny"),
    }