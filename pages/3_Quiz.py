import streamlit as st

from db.repository import get_answer_for_question, get_random_question
from services.evaluar import evaluar_respuesta
from startup import inicializar_app
from ui import aplicar_estilos, encabezado

inicializar_app()
aplicar_estilos()

encabezado("Quiz", "Pon a prueba tus conocimientos con preguntas aleatorias")

if "quiz_pregunta" not in st.session_state:
    st.session_state.quiz_pregunta = None
if "quiz_resultado" not in st.session_state:
    st.session_state.quiz_resultado = None

if st.button("Iniciar quiz", type="primary"):
    pregunta = get_random_question()
    if pregunta is None:
        st.error("No hay preguntas disponibles en la base de conocimiento.")
    else:
        st.session_state.quiz_pregunta = pregunta
        st.session_state.quiz_resultado = None
        st.rerun()

if st.session_state.quiz_pregunta:
    st.info(f"**Pregunta:** {st.session_state.quiz_pregunta}")
    respuesta_usuario = st.text_area(
        "Tu respuesta",
        height=120,
        placeholder="Escribe tu respuesta aqui...",
    )

    if st.button("Enviar respuesta"):
        respuesta_correcta = get_answer_for_question(st.session_state.quiz_pregunta)
        if not respuesta_correcta:
            st.error("No se encontro la respuesta correcta para esta pregunta.")
        else:
            estado, similitud = evaluar_respuesta(respuesta_usuario, respuesta_correcta)
            st.session_state.quiz_resultado = {
                "estado": estado,
                "similitud": similitud,
                "respuesta_correcta": respuesta_correcta,
            }

    if st.session_state.quiz_resultado:
        resultado = st.session_state.quiz_resultado
        estado = resultado["estado"]
        if estado == "correcto":
            st.success(
                f"**Estado:** {estado} · **Similitud:** {resultado['similitud']:.3f}"
            )
        elif estado == "incompleto":
            st.warning(
                f"**Estado:** {estado} · **Similitud:** {resultado['similitud']:.3f}"
            )
        else:
            st.error(
                f"**Estado:** {estado} · **Similitud:** {resultado['similitud']:.3f}"
            )
        st.markdown(f"**Respuesta correcta:** {resultado['respuesta_correcta']}")
