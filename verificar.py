#!/usr/bin/env python3
"""Verificacion del checklist de aceptacion (ejecutar con DATABASE_URL configurada)."""

import os
import sys

os.environ.setdefault(
    "DATABASE_URL",
    "postgresql+psycopg2://chatbot:chatbot@127.0.0.1:5433/chatbot",
)


def test_unitarios():
    from services.math_engine import resolver_matematica
    from services.normalize import normalizar
    from services.evaluar import evaluar_respuesta
    from db.repository import parse_data_file
    from pathlib import Path

    assert resolver_matematica("cuanto es 5 mas 3") == "El resultado es: 8.0"
    assert resolver_matematica("cuanto es 10 por 5") == "El resultado es: 50.0"
    assert normalizar("¿Qué es Python?") == "que es python"
    estado, _ = evaluar_respuesta("machine learning", "El Machine Learning es una rama de la IA")
    assert estado in ("correcto", "incompleto", "incorrecto")
    pares = parse_data_file(Path("data/ia.txt"))
    assert len(pares) >= 9
    print("[OK] Tests unitarios")


def test_integracion():
    import db.models  # noqa: F401
    from db.engine import crear_tablas
    from db.repository import (
        get_all_knowledge_pairs,
        get_dashboard_metrics,
        insert_knowledge_pair,
        seed_from_files_if_empty,
    )
    from services import embedding_engine
    from services.chat import procesar_pregunta

    crear_tablas()
    seed_from_files_if_empty()
    pares = get_all_knowledge_pairs()
    assert len(pares) >= 40, f"Se esperaban ~42 pares, hay {len(pares)}"
    preguntas = [p[0] for p in pares]
    respuestas = [p[1] for p in pares]
    embedding_engine.load_knowledge(preguntas, respuestas)

    r1 = procesar_pregunta("cuanto es 5 mas 3")
    assert r1.tipo == "matematica" and r1.similitud == 1.0

    r2 = procesar_pregunta("que es el machine learning")
    assert r2.tipo == "embedding"

    r3 = procesar_pregunta("cual es la capital de marte")
    assert r3.tipo == "ninguna"

    insert_knowledge_pair("test", "pregunta de prueba xyz", "respuesta de prueba abc")
    embedding_engine.add_knowledge("pregunta de prueba xyz", "respuesta de prueba abc")
    r4 = procesar_pregunta("pregunta de prueba xyz")
    assert r4.tipo == "embedding"

    metricas = get_dashboard_metrics()
    assert metricas.total >= 4
    print("[OK] Tests de integracion")


if __name__ == "__main__":
    test_unitarios()
    try:
        test_integracion()
        print("\nTodos los tests pasaron.")
    except Exception as exc:
        print(f"\n[WARN] Integracion omitida o fallida: {exc}", file=sys.stderr)
        print("Configura DATABASE_URL y asegurate de que PostgreSQL este activo.")
        sys.exit(1 if "connection" not in str(exc).lower() else 0)
