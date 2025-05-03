import re
import os
import logging
from typing import Optional
from telethon import events
from models.user import User
from services.auth_service import AuthService
from services.storage_service import StorageService
from services.telegram_service import TelegramService
from services.commands import CommandHandler
from services.commands.cancel_command import CancelCommand
from services.commands.add_command import AddCommand
from services.commands.remove_command import RemoveCommand
from services.commands.list_command import ListCommand
from config.constants import AUTH_PASSWORD

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MessageProcessorService:
    def __init__(self, telegram_service: TelegramService, auth_service: AuthService, storage_service: StorageService, auth_password: str):
        self.telegram_service = telegram_service
        self.auth_service = auth_service
        self.storage_service = storage_service
        self.auth_password = auth_password
        self.command_handler = self._initialize_command_handler()
        
        # Mensagem de boas-vindas
        self.welcome_message = (
            "✅ Autenticado com sucesso!\n\n"
            "Você pode gerenciar suas palavras-chave com os comandos abaixo:\n\n"
            "🟢 Adicionar palavras-chave:\n"
            "Digite:\n"
            "/adicionar palavra1, palavra2, palavra3\n"
            "Exemplo:\n"
            "/adicionar sapato, ps5, tv, cupom shopee\n\n"
            "🔴 Remover palavras-chave:\n"
            "Digite:\n"
            "/remover\n\n"
            "📋 Listar palavras-chave:\n"
            "Digite:\n"
            "/listar\n\n"
            "❌ Cancelar operação:\n"
            "Digite:\n"
            "/cancelar"
        )

    def _initialize_command_handler(self) -> CommandHandler:
        """Inicializa e configura o gerenciador de comandos"""
        handler = CommandHandler()
        handler.register_command("cancelar", CancelCommand())
        handler.register_command("adicionar", AddCommand(self.storage_service))
        handler.register_command("remover", RemoveCommand(self.storage_service))
        handler.register_command("listar", ListCommand(self.storage_service))
        return handler

    async def setup_handlers(self):
        """Configura os handlers de mensagens"""
        if not self.telegram_service.bot_client or not self.telegram_service.user_client:
            raise RuntimeError("Clientes do Telegram não inicializados")
        
        # Handler para mensagens do bot
        self.telegram_service.bot_client.add_event_handler(
            self._handle_bot_message,
            events.NewMessage
        )
        
        # Handler para mensagens do grupo
        self.telegram_service.user_client.add_event_handler(
            self._handle_group_message,
            events.NewMessage
        )

    async def _handle_bot_message(self, event: events.NewMessage.Event) -> None:
        """Processa mensagens recebidas pelo bot"""
        try:
            user_id = event.sender_id
            msg = event.message.message.strip().lower()

            if not await self._handle_authentication(user_id, msg, event):
                return

            user = self.auth_service.get_user(user_id)
            if not user:
                logger.error(f"Usuário {user_id} não encontrado após autenticação")
                return

            await self._process_commands(user, msg, event)

        except Exception as e:
            logger.error(f"Erro ao processar mensagem do bot: {e}")
            await event.reply("⚠️ Ocorreu um erro ao processar seu comando.")

    async def _handle_authentication(self, user_id: int, msg: str, event: events.NewMessage.Event) -> bool:
        if not self.auth_service.is_authenticated(user_id):
            if msg == self.auth_password:
                user = self.auth_service.authenticate_user(user_id, self.auth_password, AUTH_PASSWORD)
                self.storage_service.add_user(user_id)
                await event.reply(self.welcome_message)
                return True
            else:
                await event.reply("🔒 Senha incorreta. Tente novamente.")
                return False
        return True

    async def _process_commands(self, user: User, msg: str, event: events.NewMessage.Event) -> None:
        """Processa os comandos do usuário de forma segura"""
        try:
            # Prepara os argumentos base que todos os comandos podem precisar
            command_args = {
                'user': user,
                'event': event,
                'msg': msg
            }

            if msg.startswith('/'):
                command = msg[1:].split()[0]
                
                if await self.command_handler.handle(command, **command_args):
                    return

            if user.state == "removendo":
                await self.command_handler.handle(
                    "remover",
                    **command_args,
                    is_state_removing=True
                )
            
        except Exception as e:
            logger.error(f"Erro ao processar comando: {str(e)}")
            await event.reply("⚠️ Ocorreu um erro ao processar seu comando.")

    async def _handle_group_message(self, event: events.NewMessage.Event) -> None:
        """Processa mensagens recebidas nos grupos monitorados"""
        try:
            if event.sender_id == self.telegram_service.destination_entity.id:
                return

            message_text = event.message.text.lower() if event.message.text else ""
            
            if not (re.search(r'\d+', message_text) and 
                   re.search(r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+', message_text)):
                return

            await self._notify_users_about_keywords(event, message_text)

        except Exception as e:
            logger.error(f"Erro ao processar mensagem do grupo: {e}")

    async def _notify_users_about_keywords(self, event: events.NewMessage.Event, message_text: str) -> None:
        """Notifica usuários quando suas palavras-chave são encontradas"""
        for user_id, keywords in self.storage_service.users_data.items():
            for keyword in keywords:
                if self._is_keyword_in_message(keyword, message_text):
                    await self._send_notification(user_id, keyword, event)

    def _is_keyword_in_message(self, keyword: str, message_text: str) -> bool:
        """Verifica se a palavra-chave está presente na mensagem"""
        patterns = [
            rf'\b{re.escape(keyword)}\b',
            rf'\b{re.escape(keyword.replace(" ", "-"))}\b',
            rf'\b{re.escape(keyword.replace(" ", ""))}\b'
        ]
        return any(re.search(pattern, message_text) for pattern in patterns)

    async def _send_notification(self, user_id: str, keyword: str, event: events.NewMessage.Event) -> None:
        """Envia notificação para o usuário sobre palavra-chave encontrada"""
        try:
            caption = f"📢 Palavra-chave '{keyword}' encontrada:\n\n{event.message.text}"

            if event.message.media:
                file_path = await self._download_media(event)
                if file_path:
                    await self._send_media_message(user_id, file_path, caption)
                    os.remove(file_path)
            else:
                await self.telegram_service.bot_client.send_message(
                    int(user_id),
                    caption
                )

            logger.info(f"Notificação enviada para usuário {user_id}")

        except Exception as e:
            logger.error(f"Falha ao enviar notificação para {user_id}: {e}")

    async def _download_media(self, event: events.NewMessage.Event) -> Optional[str]:
        """Faz download de mídia anexada à mensagem"""
        try:
            os.makedirs("temp_media", exist_ok=True)
            return await self.telegram_service.user_client.download_media(
                event.message,
                file="temp_media/"
            )
        except Exception as e:
            logger.error(f"Erro ao baixar mídia: {e}")
            return None

    async def _send_media_message(self, user_id: str, file_path: str, caption: str) -> None:
        """Envia mensagem com mídia para o usuário"""
        await self.telegram_service.bot_client.send_file(
            int(user_id),
            file=file_path,
            caption=caption,
            force_document=False
        )