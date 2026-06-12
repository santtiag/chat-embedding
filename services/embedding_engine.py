from dataclasses import dataclass
from typing import Optional

import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

from config import get_settings

_preguntas: list[str] = []
_respuestas: list[str] = []
_embeddings: Optional[np.ndarray] = None
_modelo: Optional[SentenceTransformer] = None


@dataclass
class BuscarResultado:
    respuesta: str
    tipo: str
    similitud: float


def _get_model() -> SentenceTransformer:
    global _modelo
    if _modelo is None:
        cfg = get_settings()
        print(f"[embedding] Cargando modelo: {cfg.EMBEDDING_MODEL} ...")
        _modelo = SentenceTransformer(cfg.EMBEDDING_MODEL)
        print("[embedding] Modelo listo.")
    return _modelo


def load_knowledge(preguntas_list: list[str], respuestas_list: list[str]) -> None:
    """Carga (o recarga) todo el conocimiento en memoria como embeddings."""
    global _embeddings
    _preguntas.clear()
    _respuestas.clear()
    _preguntas.extend(preguntas_list)
    _respuestas.extend(respuestas_list)

    if not _preguntas:
        _embeddings = None
        print("[embedding] No hay conocimiento para vectorizar.")
        return

    modelo = _get_model()
    print(f"[embedding] Vectorizando {len(_preguntas)} pares de conocimiento...")
    _embeddings = modelo.encode(
        _preguntas,
        convert_to_numpy=True,
        show_progress_bar=False,
    )
    print("[embedding] Conocimiento vectorizado y cargado en memoria.")


def add_knowledge(pregunta: str, respuesta: str) -> None:
    """Agrega un unico par de conocimiento en caliente sin recalcular todo."""
    global _embeddings
    _preguntas.append(pregunta)
    _respuestas.append(respuesta)

    if _embeddings is not None and len(_embeddings) > 0:
        modelo = _get_model()
        emb = modelo.encode([pregunta], convert_to_numpy=True)
        _embeddings = np.vstack([_embeddings, emb])
    else:
        load_knowledge([pregunta], [respuesta])


def buscar_respuesta(pregunta: str) -> Optional[BuscarResultado]:
    """Busca la respuesta mas similar usando embeddings."""
    if _embeddings is None or len(_preguntas) == 0:
        return None

    modelo = _get_model()
    emb_pregunta = modelo.encode([pregunta], convert_to_numpy=True)
    similitudes = cosine_similarity(emb_pregunta, _embeddings)[0]

    indice = int(np.argmax(similitudes))
    score = float(similitudes[indice])

    if score >= get_settings().EMBEDDING_THRESHOLD:
        return BuscarResultado(
            _respuestas[indice],
            "embedding",
            round(score, 3),
        )
    return None
