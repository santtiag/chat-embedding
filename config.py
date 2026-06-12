import os
from urllib.parse import urlparse

from dotenv import load_dotenv
from pydantic import ValidationError, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv(override=True)


def normalizar_database_url(url: str) -> str:
    """
    Adapta URLs de Neon al formato SQLAlchemy + psycopg2.

    Neon suele entregar: postgresql://user:pass@ep-....neon.tech/neondb?sslmode=require
    SQLAlchemy sync necesita: postgresql+psycopg2://...
    """
    url = url.strip()
    if url.startswith("postgres://"):
        url = "postgresql+psycopg2://" + url[len("postgres://") :]
    elif url.startswith("postgresql://") and "+psycopg2" not in url.split("://", 1)[0]:
        url = "postgresql+psycopg2://" + url[len("postgresql://") :]

    url = url.replace("channel_binding=require", "channel_binding=prefer")
    return url


def _cargar_secrets_streamlit() -> None:
    """Carga secrets de Streamlit Cloud en variables de entorno si existen."""
    try:
        import streamlit as st

        for clave in ("DATABASE_URL", "EMBEDDING_MODEL", "EMBEDDING_THRESHOLD"):
            if clave in st.secrets:
                os.environ[clave] = str(st.secrets[clave])
    except Exception:
        pass


_cargar_secrets_streamlit()


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    DATABASE_URL: str
    EMBEDDING_MODEL: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    EMBEDDING_THRESHOLD: float = 0.35

    @field_validator("DATABASE_URL")
    @classmethod
    def validar_url(cls, valor: str) -> str:
        normalizada = normalizar_database_url(valor)
        parsed = urlparse(normalizada.replace("postgresql+psycopg2", "postgresql", 1))
        if not parsed.hostname:
            raise ValueError("DATABASE_URL invalida: falta hostname")

        if parsed.hostname in ("127.0.0.1", "localhost"):
            raise ValueError(
                "DATABASE_URL apunta a localhost. "
                "Pega tu URL de Neon en .env (postgresql://...@ep-....neon.tech/...)."
            )
        if "ep-xxxx" in normalizada or "USER:PASSWORD" in normalizada:
            raise ValueError(
                "DATABASE_URL sigue siendo el ejemplo de .env.example. "
                "Copia la connection string real desde console.neon.tech."
            )
        if parsed.password and len(parsed.password) < 12:
            raise ValueError(
                "La contraseña en DATABASE_URL parece incompleta (muy corta). "
                "Usa el boton Copy de Neon y ejecuta: uv run python setup_env.py"
            )
        return normalizada


_settings: Settings | None = None
_config_error: str | None = None

try:
    _settings = Settings()
except ValidationError as exc:
    _config_error = exc.errors()[0]["msg"] if exc.errors() else str(exc)


def obtener_error_configuracion() -> str | None:
    return _config_error


def get_settings() -> Settings:
    if _settings is None:
        raise RuntimeError(
            _config_error
            or "DATABASE_URL no configurada. Edita el archivo .env con tu URL de Neon."
        )
    return _settings


# Compatibilidad con imports existentes que usan settings.EMBEDDING_MODEL
settings = _settings
