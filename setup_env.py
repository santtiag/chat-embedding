#!/usr/bin/env python3
"""Escribe DATABASE_URL en .env a partir de la connection string de Neon."""

import re
import sys
from pathlib import Path
from urllib.parse import urlparse

ENV_PATH = Path(__file__).resolve().parent / ".env"
EXAMPLE_PATH = Path(__file__).resolve().parent / ".env.example"


def validar_url(database_url: str) -> None:
    database_url = database_url.strip()
    if not database_url.startswith(("postgresql://", "postgres://", "postgresql+psycopg2://")):
        raise SystemExit("La URL debe empezar con postgresql:// o postgres://")
    if "ep-xxxx" in database_url or "USER:PASSWORD" in database_url:
        raise SystemExit("Pega la URL real de Neon, no el ejemplo.")
    parsed = urlparse(database_url.replace("postgresql+psycopg2", "postgresql", 1))
    if not parsed.hostname or "neon.tech" not in parsed.hostname:
        raise SystemExit("El hostname no parece ser de Neon (.neon.tech).")
    if not parsed.password or len(parsed.password) < 12:
        raise SystemExit(
            f"La contraseña parece incompleta (longitud {len(parsed.password or '')}). "
            "Copia la URL con el boton Copy de console.neon.tech — no la escribas a mano."
        )


def escribir_env(database_url: str) -> None:
    validar_url(database_url)
    database_url = database_url.strip()

    plantilla = EXAMPLE_PATH.read_text(encoding="utf-8") if EXAMPLE_PATH.exists() else ""
    if "DATABASE_URL=" in plantilla:
        contenido = re.sub(
            r"^DATABASE_URL=.*$",
            f"DATABASE_URL={database_url}",
            plantilla,
            count=1,
            flags=re.MULTILINE,
        )
    else:
        contenido = (
            f"DATABASE_URL={database_url}\n"
            "EMBEDDING_MODEL=sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2\n"
            "EMBEDDING_THRESHOLD=0.35\n"
        )

    ENV_PATH.write_text(contenido, encoding="utf-8")
    print(f"Guardado en {ENV_PATH}")
    print("Prueba la conexion con: uv run python setup_env.py --test")


def probar_conexion() -> None:
    import db.models  # noqa: F401
    from db.engine import crear_tablas
    from sqlalchemy import text
    from db.engine import get_engine

    crear_tablas()
    with get_engine().connect() as conn:
        pares = conn.execute(text("SELECT COUNT(*) FROM knowledge_pairs")).scalar()
    print(f"Conexion OK. Pares en DB: {pares}")


def main() -> None:
    if len(sys.argv) >= 2 and sys.argv[1] == "--test":
        probar_conexion()
        return

    if len(sys.argv) >= 2:
        url = sys.argv[1]
    else:
        print("Pega tu connection string COMPLETA de Neon (boton Copy) y presiona Enter:")
        url = input().strip()

    escribir_env(url)


if __name__ == "__main__":
    main()
