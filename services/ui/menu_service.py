import logging

from services.ui import keyboards as kb

logger = logging.getLogger(__name__)

MENU_TEXT = "🤖 *FindPromotion*\nEscolha uma opção:"


class MenuService:
    """Telas com botões inline (menu, lista, adicionar, remover)."""

    def __init__(self, auth_service, storage_service):
        self.auth_service = auth_service
        self.storage_service = storage_service

    # ---------- telas ----------
    async def show_menu(self, event, edit=False):
        send = event.edit if edit else event.reply
        await send(MENU_TEXT, buttons=kb.main_menu(), parse_mode="md")

    async def _show_list(self, event, user, page):
        keywords = self.storage_service.get_user_keywords(user.id)
        if not keywords:
            await event.edit(
                "📋 Sua lista está vazia.",
                buttons=[[kb.Button.inline("➕ Adicionar", b"add:start")], kb.back_row()],
            )
            return
        rows, page = kb.list_keyboard(keywords, page)
        text = "📋 *Suas palavras-chave* ({}):\n\n".format(len(keywords))
        chunk, _, _ = kb.paginate(keywords, page)
        text += "\n".join(f"• {w}" for w in chunk)
        await event.edit(text, buttons=rows, parse_mode="md")

    async def _show_remove(self, event, user, page):
        keywords = self.storage_service.get_user_keywords(user.id)
        if not keywords:
            await event.edit("📋 Sua lista está vazia.", buttons=[kb.back_row()])
            return
        rows, _ = kb.remove_keyboard(keywords, page)
        await event.edit("🗑️ Toque na palavra que deseja remover:", buttons=rows)

    async def _start_add(self, event, user):
        user.state = "adicionando"
        await event.edit(
            "➕ Envie as palavras-chave separadas por vírgula.\n"
            "Exemplo: `ps5, tv, cupom shopee`",
            buttons=kb.cancel_keyboard(),
            parse_mode="md",
        )

    # ---------- entrada de texto (estado "adicionando") ----------
    async def handle_add_text(self, user, event, msg):
        added = []
        for word in msg.split(","):
            word = word.strip()
            if word and self.storage_service.add_keyword_to_user(user.id, word):
                added.append(word)
        user.state = None
        text = "Palavras adicionadas ✅: " + (", ".join(added) if added else "Nenhuma (já existiam)")
        await event.reply(text, buttons=kb.after_add_keyboard())

    # ---------- callbacks ----------
    async def handle_callback(self, event):
        user = self.auth_service.get_user(event.sender_id)
        if not user:
            await event.answer("🔒 Envie a senha primeiro.", alert=True)
            return

        data = event.data.decode("utf-8")
        parts = data.split(":")
        action = parts[0]

        if action == "noop":
            await event.answer()
            return

        if action == "menu":
            user.state = None
            await self.show_menu(event, edit=True)
        elif action == "cancel":
            user.state = None
            await event.edit("❌ Operação cancelada.", buttons=kb.main_menu())
        elif action == "add":
            await self._start_add(event, user)
        elif action == "list":
            user.state = None
            await self._show_list(event, user, int(parts[1]))
        elif action == "rm":
            user.state = None
            await self._handle_remove(event, user, parts)
        else:
            logger.warning(f"Callback desconhecido: {data}")
        await event.answer()

    async def _handle_remove(self, event, user, parts):
        sub = parts[1]
        keywords = self.storage_service.get_user_keywords(user.id)

        if sub.isdigit():
            await self._show_remove(event, user, int(sub))
            return

        word = next((w for w in keywords if kb.word_id(w) == parts[2]), None)
        if word is None:
            await event.edit("⚠️ Essa palavra não está mais na lista.", buttons=[kb.back_row()])
            return

        if sub == "ask":
            await event.edit(
                f"Remover a palavra *{word}*?",
                buttons=kb.confirm_remove_keyboard(parts[2]),
                parse_mode="md",
            )
        elif sub == "do":
            self.storage_service.remove_keyword_from_user(user.id, word)
            await self._show_remove(event, user, 0)
