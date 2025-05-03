from telethon import TelegramClient

class TelegramService:
    def __init__(self, secrets):
        self.secrets = secrets
        self.bot_client = None
        self.user_client = None
        self.destination_entity = None
    
    async def initialize(self):
        """Inicializa os clientes do Telegram"""
        self.bot_client = await TelegramClient(
            'bot_session', 
            self.secrets["api_id"], 
            self.secrets["api_hash"]
        ).start(bot_token=self.secrets["bot_token"])
        
        self.user_client = TelegramClient(
            'session_name',
            self.secrets["api_id"],
            self.secrets["api_hash"]
        )
        await self.user_client.start(self.secrets["phone_number"])
        
        self.destination_entity = await self.user_client.get_entity(
            self.secrets["destino"]
        )
        return self  # Retorna a própria instância para encadeamento
    
    async def run(self):
        """Mantém os clientes em execução"""
        await self.user_client.run_until_disconnected()