"""Normalização de texto para buscas e comparações tolerantes (B06).

"Verão", "VERAO" e "  verao " viram "verao": sem acentos, minúsculas e espaços
simples. Funciona igual em SQLite (desenvolvimento) e PostgreSQL (produção).
"""
import unicodedata


def normalizar(texto: str | None) -> str:
    if not texto:
        return ""
    sem_acentos = "".join(
        c for c in unicodedata.normalize("NFKD", texto) if not unicodedata.combining(c)
    )
    return " ".join(sem_acentos.casefold().split())
