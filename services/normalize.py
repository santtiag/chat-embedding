import re
import unicodedata


def normalizar(texto: str) -> str:
    """Normaliza texto para comparación."""
    texto = unicodedata.normalize("NFD", texto)
    texto = re.sub(r"[̀-ͯ]", "", texto)
    texto = re.sub(r"[^a-z0-9 ]", "", texto.lower())
    texto = re.sub(r"\s+", " ", texto).strip()
    return texto
