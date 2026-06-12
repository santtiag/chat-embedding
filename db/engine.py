from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()
_engine = None
_session_maker = None


def _ensure_engine():
    global _engine, _session_maker
    if _engine is None:
        from config import get_settings

        _engine = create_engine(get_settings().DATABASE_URL, pool_pre_ping=True)
        _session_maker = sessionmaker(bind=_engine)


class _SessionLocalFactory:
    def __call__(self):
        _ensure_engine()
        return _session_maker()


SessionLocal = _SessionLocalFactory()


def get_engine():
    _ensure_engine()
    return _engine


def crear_tablas() -> None:
    """Crea las tablas si no existen."""
    Base.metadata.create_all(get_engine())
