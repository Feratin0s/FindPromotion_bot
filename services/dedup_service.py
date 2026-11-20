import hashlib
import re
import time
from collections import OrderedDict
from typing import Callable, Iterable, List, Optional

URL_RE = re.compile(r"https?://[^\s<>\"')\]]+", re.IGNORECASE)
MIN_TEXT_LEN = 20  # textos muito curtos não geram chave de texto (evita falso positivo)


def normalize_url(url: str) -> str:
    url = url.strip().rstrip(".,;:!?)")
    url = re.sub(r"^https?://(www\.)?", "", url.lower())
    url = url.split("#", 1)[0].split("?", 1)[0]
    return url.rstrip("/")


def fingerprint_keys(text: Optional[str], chat_id=None, msg_id=None) -> List[str]:
    """Chaves que identificam um anúncio: id da mensagem, links e texto normalizado."""
    text = text or ""
    keys = []
    if chat_id is not None and msg_id is not None:
        keys.append(f"msg:{chat_id}:{msg_id}")

    for url in URL_RE.findall(text):
        norm = normalize_url(url)
        if norm:
            keys.append(f"url:{norm}")

    body = re.sub(r"[^a-z0-9à-ú]", "", URL_RE.sub(" ", text.lower()))
    if len(body) >= MIN_TEXT_LEN:
        keys.append("txt:" + hashlib.sha1(body.encode("utf-8")).hexdigest())
    return keys


class DedupService:
    """Lembra anúncios já enviados por usuário, por um tempo limitado (TTL)."""

    def __init__(self, ttl_seconds: int = 6 * 3600, max_entries: int = 5000,
                 clock: Callable[[], float] = time.monotonic):
        self.ttl = ttl_seconds
        self.max_entries = max_entries
        self.clock = clock
        self._seen: "OrderedDict[tuple, float]" = OrderedDict()

    def _purge(self, now: float) -> None:
        while self._seen:
            key, ts = next(iter(self._seen.items()))
            if now - ts > self.ttl or len(self._seen) > self.max_entries:
                self._seen.popitem(last=False)
            else:
                break

    def check_and_mark(self, user_id, keys: Iterable[str]) -> bool:
        """Retorna True se o anúncio é duplicado. Caso contrário marca como visto.

        Síncrono de propósito: sem `await` entre checar e marcar, então dois
        eventos concorrentes do mesmo anúncio não passam juntos.
        """
        keys = list(keys)
        now = self.clock()
        self._purge(now)
        uid = str(user_id)
        if any((uid, k) in self._seen for k in keys):
            for k in keys:  # renova a validade
                self._seen[(uid, k)] = now
                self._seen.move_to_end((uid, k))
            return True
        for k in keys:
            self._seen[(uid, k)] = now
        return False

    def forget(self, user_id, keys: Iterable[str]) -> None:
        """Desfaz a marcação (ex.: falha no envio, para permitir nova tentativa)."""
        for k in keys:
            self._seen.pop((str(user_id), k), None)
