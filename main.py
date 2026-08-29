import asyncio
import os
from dotenv import load_dotenv
from telethon import TelegramClient, events
from config.secrets import load_secrets
from services.telegram_service import TelegramService
from services.message_processor_service import MessageProcessorService
from services.auth_service import AuthService
from services.storage_service import StorageService

load_dotenv()

AUTH_PASSWORD = os.getenv('AUTH_PASSWORD')

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
    
    await message_processor.setup_handlers()
    print("✅ Bot rodando e monitorando mensagens...")
    await telegram_service.run()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())