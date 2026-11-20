import asyncio
import os
import sys
import tempfile
from pathlib import Path
from types import SimpleNamespace

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
os.environ.setdefault("KEYWORDS_FILE", os.path.join(tempfile.mkdtemp(), "keywords_test.json"))

from services.auth_service import AuthService  # noqa: E402
from services.dedup_service import DedupService, fingerprint_keys, normalize_url  # noqa: E402
from services.message_processor_service import MessageProcessorService  # noqa: E402
from services.storage_service import StorageService  # noqa: E402

AD = (
    "🌟 Exclusivo Prime 🌟\n\nFinish Powerball Detergente Lava Louças 91 tabletes\n"
    "Por: R$ 114,44\nCompre em: https://link.amazon/B0ckElzfu"
)


class FakeEvent:
    def __init__(self, text, chat_id=-100, msg_id=1, sender_id=5):
        self.sender_id = sender_id
        self.chat_id = chat_id
        self.message = SimpleNamespace(message=text, text=text, media=None, id=msg_id)


class FakeBot:
    def __init__(self):
        self.sent = []

    async def send_message(self, user_id, text, **kwargs):
        self.sent.append({"user_id": user_id, "text": text})


@pytest.fixture
def storage(tmp_path, monkeypatch):
    monkeypatch.setattr("services.storage_service.KEYWORDS_FILE", str(tmp_path / "k.json"))
    return StorageService()


@pytest.fixture
def processor(storage):
    tg = SimpleNamespace(
        bot_client=FakeBot(),
        user_client=SimpleNamespace(),
        destination_entity=SimpleNamespace(id=999),
    )
    return MessageProcessorService(tg, AuthService(), storage, "senha")


def add_keywords(storage, user_id, *words):
    storage.add_user(user_id)
    for w in words:
        storage.add_keyword_to_user(user_id, w)


def group_msg(processor, text, **kw):
    asyncio.run(processor._handle_group_message(FakeEvent(text, **kw)))


def sent(processor):
    return processor.telegram_service.bot_client.sent


# ---------- duplicado na mesma mensagem ----------
def test_two_keywords_one_notification(processor, storage):
    add_keywords(storage, 1, "detergente", "lava louças")
    group_msg(processor, AD)
    assert len(sent(processor)) == 1
    text = sent(processor)[0]["text"]
    assert "'detergente'" in text and "'lava louças'" in text
    assert text.startswith("📢 Palavras-chave")


def test_single_keyword_label_singular(processor, storage):
    add_keywords(storage, 1, "detergente")
    group_msg(processor, AD)
    assert sent(processor)[0]["text"].startswith("📢 Palavra-chave 'detergente'")


# ---------- mesmo anúncio repetido ----------
def test_same_message_event_twice(processor, storage):
    add_keywords(storage, 1, "detergente")
    group_msg(processor, AD, msg_id=7)
    group_msg(processor, AD, msg_id=7)
    assert len(sent(processor)) == 1


def test_same_ad_reposted_in_other_group(processor, storage):
    add_keywords(storage, 1, "detergente")
    group_msg(processor, AD, chat_id=-1, msg_id=1)
    group_msg(processor, AD, chat_id=-2, msg_id=99)
    assert len(sent(processor)) == 1


def test_same_link_different_wording(processor, storage):
    add_keywords(storage, 1, "detergente")
    group_msg(processor, "Detergente 10 reais https://amzn.to/abc?tag=x", msg_id=1)
    group_msg(processor, "OFERTA detergente 10 reais!! https://www.amzn.to/abc/", msg_id=2)
    assert len(sent(processor)) == 1


def test_price_change_is_new_ad(processor, storage):
    add_keywords(storage, 1, "detergente")
    group_msg(processor, AD, msg_id=1)
    group_msg(processor, AD.replace("114,44", "89,90").replace("B0ckElzfu", "Nova123"), msg_id=2)
    assert len(sent(processor)) == 2


def test_different_ads_both_sent(processor, storage):
    add_keywords(storage, 1, "ps5")
    group_msg(processor, "PS5 por R$ 3000 https://loja.com/ps5-a", msg_id=1)
    group_msg(processor, "PS5 Slim por R$ 2800 https://outra.com/ps5-b", msg_id=2)
    assert len(sent(processor)) == 2


def test_dedup_is_per_user(processor, storage):
    add_keywords(storage, 1, "ps5")
    add_keywords(storage, 2, "ps5")
    group_msg(processor, "PS5 por R$ 3000 https://loja.com/ps5-a")
    assert sorted(m["user_id"] for m in sent(processor)) == [1, 2]


def test_failed_send_can_retry(processor, storage):
    add_keywords(storage, 1, "ps5")
    bot = processor.telegram_service.bot_client
    original = bot.send_message

    async def boom(*a, **k):
        raise RuntimeError("falha")

    bot.send_message = boom
    group_msg(processor, "PS5 por R$ 3000 https://loja.com/ps5-a", msg_id=1)
    bot.send_message = original
    group_msg(processor, "PS5 por R$ 3000 https://loja.com/ps5-a", msg_id=1)
    assert len(sent(processor)) == 1


# ---------- unidade ----------
def test_ttl_expires():
    now = [0]
    d = DedupService(ttl_seconds=10, clock=lambda: now[0])
    keys = ["url:a.com/x"]
    assert d.check_and_mark(1, keys) is False
    assert d.check_and_mark(1, keys) is True
    now[0] = 11
    assert d.check_and_mark(1, keys) is False


def test_max_entries_bounded():
    d = DedupService(max_entries=3)
    for i in range(10):
        d.check_and_mark(1, [f"url:{i}"])
    assert len(d._seen) <= 4


def test_normalize_url():
    assert normalize_url("https://www.Amzn.to/abc/?tag=1#x") == "amzn.to/abc"
    assert normalize_url("http://a.com/p).") == "a.com/p"


def test_short_text_has_no_text_key():
    assert not any(k.startswith("txt:") for k in fingerprint_keys("ps5 99 http://a.com/x"))
