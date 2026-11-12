import asyncio
import os
import urllib.request
from dotenv import load_dotenv
from telethon import TelegramClient, events
from config.secrets import load_secrets
from services.telegram_service import TelegramService
from services.message_processor_service import MessageProcessorService
from services.auth_service import AuthService
from services.storage_service import StorageService

load_dotenv()
AUTH_PASSWORD = os.getenv('AUTH_PASSWORD')
CORE_URL = os.getenv('CORE_URL', 'http://findpromo-core:3000').rstrip('/')

def ask_to_core(caminho):
    url = f"{CORE_URL}{caminho}"
    with urllib.request.urlopen(url, timeout=5) as resp:
        return resp.read().decode("utf-8")
   # → pong

# --------------------------------------------------
## GET (é o padrão quando você não passa dados)
#urllib.request.urlopen("http://findpromo-core:3000/ping")
#
## POST (basta passar data=, e o urllib já troca para POST sozinho)
#req = urllib.request.Request(
#    "http://findpromo-core:3000/keywords",
#    data=b"iphone",
#)
#urllib.request.urlopen(req)

async def main():
    secrets = load_secrets()
    
    telegram_service = TelegramService(secrets)
    await telegram_service.initialize()
    
    auth_service = AuthService()
    storage_service = StorageService()
    
    message_processor = MessageProcessorService(
        telegram_service=telegram_service,
        auth_service=auth_service,
        storage_service=storage_service,
        auth_password=AUTH_PASSWORD
    )

    print(ask_to_core("/ping"))

    await message_processor.setup_handlers()
    print("✅ Bot rodando e monitorando mensagens...")
    await telegram_service.run()

if __name__ == "__main__":
    asyncio.run(main())