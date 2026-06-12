"""Inicializacion compartida de base de datos y motor de embeddings."""

import streamlit as st


@st.cache_resource
def inicializar_app() -> int:
    import db.models  # noqa: F401 — registra modelos en metadata
    from db.engine import crear_tablas
    from db.repository import get_all_knowledge_pairs, seed_from_files_if_empty
    from services import embedding_engine

    crear_tablas()
    seed_from_files_if_empty()
    pares = get_all_knowledge_pairs()
    preguntas = [p[0] for p in pares]
    respuestas = [p[1] for p in pares]
    embedding_engine.load_knowledge(preguntas, respuestas)
    return len(pares)
