from db.repository import insert_query_log
from db.schemas import ChatResultado
from services.embedding_engine import buscar_respuesta
from services.math_engine import resolver_matematica

MENSAJE_SIN_RESPUESTA = (
    "Lo siento, no encontré una respuesta adecuada para tu pregunta. "
    "Intenta reformularla o consulta el explorador de temas."
)


def procesar_pregunta(pregunta: str) -> ChatResultado:
    pregunta = pregunta.strip()

    resultado_matematica = resolver_matematica(pregunta)
    if resultado_matematica:
        insert_query_log(pregunta, "matematica", 1.0)
        return ChatResultado(
            respuesta=resultado_matematica,
            tipo="matematica",
            similitud=1.0,
        )

    resultado_embedding = buscar_respuesta(pregunta)
    if resultado_embedding:
        insert_query_log(
            pregunta,
            resultado_embedding.tipo,
            resultado_embedding.similitud,
        )
        return ChatResultado(
            respuesta=resultado_embedding.respuesta,
            tipo="embedding",
            similitud=resultado_embedding.similitud,
        )

    insert_query_log(pregunta, "ninguna", 0.0)
    return ChatResultado(
        respuesta=MENSAJE_SIN_RESPUESTA,
        tipo="ninguna",
        similitud=0.0,
    )
