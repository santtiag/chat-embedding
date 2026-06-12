from dataclasses import dataclass
from typing import Literal


@dataclass
class ThemeInfo:
    nombre: str
    archivo: str
    cantidad: int
    ejemplos: list[str]


@dataclass
class DashboardData:
    metricas: dict[str, int]
    total: int
    porcentajes: dict[str, float]


@dataclass
class TopItem:
    pregunta: str
    count: int


@dataclass
class ChatResultado:
    respuesta: str
    tipo: Literal["embedding", "matematica", "ninguna"]
    similitud: float
