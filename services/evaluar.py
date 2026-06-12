import difflib
from typing import Literal

from services.normalize import normalizar


def evaluar_respuesta(
    respuesta_usuario: str,
    respuesta_correcta: str,
) -> tuple[Literal["correcto", "incompleto", "incorrecto"], float]:
    ratio = difflib.SequenceMatcher(
        None,
        normalizar(respuesta_usuario),
        normalizar(respuesta_correcta),
    ).ratio()

    if ratio >= 0.8:
        estado: Literal["correcto", "incompleto", "incorrecto"] = "correcto"
    elif ratio >= 0.5:
        estado = "incompleto"
    else:
        estado = "incorrecto"

    return estado, round(ratio, 3)
