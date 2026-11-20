import hashlib
from telethon import Button

PAGE_SIZE = 6


def word_id(word: str) -> str:
    """ID curto e estável da palavra (callback_data tem limite de 64 bytes)."""
    return hashlib.md5(word.encode("utf-8")).hexdigest()[:8]


def main_menu():
    return [
        [Button.inline("➕ Adicionar", b"add:start"), Button.inline("📋 Listar", b"list:0")],
        [Button.inline("🗑️ Remover", b"rm:0"), Button.inline("❌ Cancelar", b"cancel")],
    ]


def back_row():
    return [Button.inline("🔙 Menu", b"menu")]


def paginate(items, page):
    pages = max(1, -(-len(items) // PAGE_SIZE))
    page = max(0, min(page, pages - 1))
    start = page * PAGE_SIZE
    return items[start:start + PAGE_SIZE], page, pages


def nav_row(prefix, page, pages):
    row = []
    if page > 0:
        row.append(Button.inline("◀️", f"{prefix}:{page - 1}".encode()))
    row.append(Button.inline(f"{page + 1}/{pages}", b"noop"))
    if page < pages - 1:
        row.append(Button.inline("▶️", f"{prefix}:{page + 1}".encode()))
    return row


def list_keyboard(keywords, page):
    _, page, pages = paginate(keywords, page)
    rows = []
    if pages > 1:
        rows.append(nav_row("list", page, pages))
    rows.append([Button.inline("➕ Adicionar", b"add:start"), Button.inline("🗑️ Remover", b"rm:0")])
    rows.append(back_row())
    return rows, page


def remove_keyboard(keywords, page):
    chunk, page, pages = paginate(keywords, page)
    rows = [
        [Button.inline(f"🗑️ {w}", f"rm:ask:{word_id(w)}".encode())] for w in chunk
    ]
    if pages > 1:
        rows.append(nav_row("rm", page, pages))
    rows.append(back_row())
    return rows, page


def confirm_remove_keyboard(wid):
    return [
        [
            Button.inline("✅ Sim", f"rm:do:{wid}".encode()),
            Button.inline("❌ Não", b"rm:0"),
        ]
    ]


def cancel_keyboard():
    return [[Button.inline("❌ Cancelar", b"cancel")]]


def after_add_keyboard():
    return [
        [Button.inline("➕ Adicionar mais", b"add:start"), Button.inline("📋 Listar", b"list:0")],
        back_row(),
    ]
