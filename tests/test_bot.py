import asyncio
from types import SimpleNamespace

from conftest import PASSWORD, FakeEvent
from services.ui import keyboards as kb


class FakeCallback:
    def __init__(self, data, sender_id=1):
        self.sender_id = sender_id
        self.data = data.encode()
        self.edits = []
        self.answers = []

    async def edit(self, text, **kwargs):
        self.edits.append({"text": text, **kwargs})

    async def answer(self, text=None, **kwargs):
        self.answers.append(text)


def click(processor, data, sender_id=1):
    ev = FakeCallback(data, sender_id)
    asyncio.run(processor.menu_service.handle_callback(ev))
    return ev


def buttons_data(buttons):
    return [b.type.data.decode() for row in buttons for b in row]


# ---------- autenticação / loop ----------
def test_wrong_password_rejected(send):
    assert "incorreta" in send("qualquer").replies[0]["text"]


def test_login_shows_menu_buttons(send):
    ev = send(PASSWORD)
    assert "Autenticado" in ev.replies[0]["text"]
    assert "add:start" in buttons_data(ev.replies[1]["buttons"])


def test_ignores_outgoing_messages(processor):
    ev = FakeEvent("🔒 Senha incorreta. Tente novamente.")
    ev.out = True
    asyncio.run(processor._handle_bot_message(ev))
    assert ev.replies == []


def test_ignores_other_bots(processor):
    ev = FakeEvent("oi")

    async def get_sender():
        return SimpleNamespace(bot=True)

    ev.get_sender = get_sender
    asyncio.run(processor._handle_bot_message(ev))
    assert ev.replies == []


def test_callback_requires_auth(processor):
    ev = click(processor, "list:0", sender_id=77)
    assert ev.edits == [] and "senha" in ev.answers[0].lower()


# ---------- comandos de texto (comportamento antigo) ----------
def test_text_commands_still_work(logged, storage):
    logged("/adicionar ps5, tv")
    assert storage.get_user_keywords(1) == ["ps5", "tv"]
    assert "ps5, tv" in logged("/listar").replies[0]["text"]


def test_start_shows_menu(logged):
    assert logged("/start").replies[0]["buttons"]


# ---------- botões ----------
def test_add_flow(logged, processor, storage):
    ev = click(processor, "add:start")
    assert processor.auth_service.get_user(1).state == "adicionando"
    assert "cancel" in buttons_data(ev.edits[0]["buttons"])
    reply = logged("sapato, cupom shopee")
    assert storage.get_user_keywords(1) == ["sapato", "cupom shopee"]
    assert "sapato" in reply.replies[0]["text"]
    assert processor.auth_service.get_user(1).state is None


def test_cancel_clears_state(logged, processor):
    click(processor, "add:start")
    click(processor, "cancel")
    assert processor.auth_service.get_user(1).state is None


def test_list_empty_and_filled(logged, processor, storage):
    assert "vazia" in click(processor, "list:0").edits[0]["text"]
    storage.add_keyword_to_user(1, "ps5")
    assert "ps5" in click(processor, "list:0").edits[0]["text"]


def test_list_pagination(logged, processor, storage):
    for i in range(kb.PAGE_SIZE + 2):
        storage.add_keyword_to_user(1, f"item{i}")
    p0 = click(processor, "list:0").edits[0]
    assert "list:1" in buttons_data(p0["buttons"])
    p1 = click(processor, "list:1").edits[0]
    assert "item7" in p1["text"] and "item0" not in p1["text"]


def test_remove_with_confirmation(logged, processor, storage):
    storage.add_keyword_to_user(1, "ps5")
    storage.add_keyword_to_user(1, "tv")
    wid = kb.word_id("ps5")
    ask = click(processor, f"rm:ask:{wid}").edits[0]
    assert "ps5" in ask["text"] and f"rm:do:{wid}" in buttons_data(ask["buttons"])
    assert storage.get_user_keywords(1) == ["ps5", "tv"]  # ainda não removeu
    click(processor, f"rm:do:{wid}")
    assert storage.get_user_keywords(1) == ["tv"]


def test_remove_stale_word(logged, processor):
    ev = click(processor, f"rm:do:{kb.word_id('inexistente')}")
    assert "não está mais" in ev.edits[0]["text"]


# ---------- notificação por palavra-chave (comportamento atual) ----------
def test_keyword_notification(logged, processor, storage):
    storage.add_keyword_to_user(1, "ps5")
    ev = FakeEvent("PS5 por 2999 https://loja.com/ps5", sender_id=5)
    asyncio.run(processor._handle_group_message(ev))
    sent = processor.telegram_service.bot_client.sent
    assert sent and sent[0]["user_id"] == 1
