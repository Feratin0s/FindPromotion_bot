import os
import sys
import tempfile
from pathlib import Path
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tests"))

# Precisa ser definido antes de importar o StorageService / .env real
os.environ["KEYWORDS_FILE"] = os.path.join(tempfile.mkdtemp(), "keywords_test.json")
os.environ["AUTH_PASSWORD"] = "senha123"

from services.auth_service import AuthService  # noqa: E402
from services.message_processor_service import MessageProcessorService  # noqa: E402
from services.storage_service import StorageService  # noqa: E402

PASSWORD = "senha123"


class FakeEvent:
    """Simula events.NewMessage.Event, guardando as respostas enviadas."""

    def __init__(self, text, sender_id=1, media=None):
        self.sender_id = sender_id
        self.message = SimpleNamespace(message=text, text=text, media=media)
        self.replies = []

    async def reply(self, text, **kwargs):
        self.replies.append({"text": text, **kwargs})


class FakeBotClient:
    def __init__(self):
        self.sent = []

    async def send_file(self, user_id, file=None, caption=None, **kwargs):
        self.sent.append({"user_id": user_id, "file": file, "caption": caption})

    async def send_message(self, user_id, text, **kwargs):
        self.sent.append({"user_id": user_id, "text": text, **kwargs})


class FakeTelegramService:
    def __init__(self):
        self.bot_client = FakeBotClient()
        self.user_client = SimpleNamespace(add_event_handler=lambda *a, **k: None)
        self.destination_entity = SimpleNamespace(id=999)


@pytest.fixture
def storage(tmp_path, monkeypatch):
    path = tmp_path / "keywords.json"
    monkeypatch.setattr("services.storage_service.KEYWORDS_FILE", str(path))
    return StorageService()


@pytest.fixture
def processor(storage, monkeypatch):
    # O processor compara com AUTH_PASSWORD lido do .env no import
    monkeypatch.setattr("services.message_processor_service.AUTH_PASSWORD", PASSWORD)
    return MessageProcessorService(
        telegram_service=FakeTelegramService(),
        auth_service=AuthService(),
        storage_service=storage,
        auth_password=PASSWORD,
    )


@pytest.fixture
def send(processor):
    """Envia uma mensagem como usuário ao bot e devolve o evento (com replies)."""
    import asyncio

    def _send(text, sender_id=1):
        event = FakeEvent(text, sender_id)
        asyncio.run(processor._handle_bot_message(event))
        return event

    return _send


@pytest.fixture
def logged(send):
    """Usuário 1 já autenticado."""
    send(PASSWORD)
    return send
