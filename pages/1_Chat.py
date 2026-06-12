import streamlit as st

from db.repository import insert_feedback
from services.chat import procesar_pregunta
from startup import inicializar_app
from ui import aplicar_estilos, encabezado, etiqueta

inicializar_app()
aplicar_estilos()

encabezado("Chat", "Conversa con el asistente basado en busqueda semantica")

if "messages" not in st.session_state:
    st.session_state.messages = []

if st.button("Nueva conversación", type="secondary"):
    st.session_state.messages = []
    st.rerun()


def _mostrar_badge(tipo: str, similitud: float) -> None:
    if tipo == "matematica":
        etiqueta("Calculo matematico")
    elif tipo == "embedding":
        etiqueta(f"Modelo semantico · similitud {similitud:.3f}")
    else:
        etiqueta("Sin coincidencia")


for mensaje in st.session_state.messages:
    with st.chat_message(mensaje["role"]):
        st.markdown(mensaje["content"])
        if mensaje["role"] == "assistant":
            _mostrar_badge(mensaje.get("tipo", "ninguna"), mensaje.get("similitud", 0.0))

if pregunta := st.chat_input("Escribe tu pregunta..."):
    st.session_state.messages.append({"role": "user", "content": pregunta})

    with st.spinner("Pensando..."):
        resultado = procesar_pregunta(pregunta)

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": resultado.respuesta,
            "tipo": resultado.tipo,
            "similitud": resultado.similitud,
            "pregunta": pregunta,
        }
    )
    st.rerun()

mensajes_bot = [m for m in st.session_state.messages if m["role"] == "assistant"]
if mensajes_bot:
    ultimo = mensajes_bot[-1]
    st.divider()
    st.subheader("Feedback")
    st.caption("Califica la última respuesta del chatbot")

    with st.form("form_feedback", clear_on_submit=True):
        calificacion = st.radio(
            "Calificación",
            options=["buena", "mala"],
            horizontal=True,
            label_visibility="collapsed",
        )
        comentario = st.text_area("Comentario (opcional)", height=80)
        enviar_feedback = st.form_submit_button("Guardar feedback")

    if enviar_feedback:
        insert_feedback(
            question=ultimo.get("pregunta", ""),
            answer=ultimo["content"],
            rating=calificacion,
            comment=comentario or None,
        )
        st.success("Gracias por tu feedback.")
