from __future__ import annotations

import re


CHAVE_RE = re.compile(r"(?<!\d)\d{44}(?!\d)")


def extract_chaves(text: str) -> list[str]:
    """
    Extrai todas as chaves de 44 dígitos encontradas no texto (SPED, logs, etc).
    Remove duplicadas e mantém ordem de aparição.
    """
    if not text:
        return []

    found = CHAVE_RE.findall(text)

    # manter ordem e remover duplicadas
    seen = set()
    out: list[str] = []
    for ch in found:
        if ch not in seen:
            seen.add(ch)
            out.append(ch)
    return out