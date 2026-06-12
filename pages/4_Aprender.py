import streamlit as st

from db.repository import get_answer_for_question, get_questions_by_topic, get_topics_with_stats
from services.evaluar import evaluar_respuesta
from startup import inicializar_app
from ui import aplicar_estilos, encabezado

inicializar_app()
aplicar_estilos()

encabezado("Aprender", "Aprendizaje guiado por tema con evaluacion de respuestas")

temas = get_topics_with_stats()
if not temas:
    st.warning("No hay temas disponibles.")
    st.stop()

opciones_temas = {t.nombre: t.archivo.replace(".txt", "") for t in temas}
tema_elegido = st.selectbox("Selecciona un tema", list(opciones_temas.keys()))
slug = opciones_temas[tema_elegido]

preguntas = get_questions_by_topic(slug)
if not preguntas:
    st.warning("Este tema no tiene preguntas.")
    st.stop()

pregunta_seleccionada = st.radio("Elige una pregunta", preguntas)
respuesta_usuario = st.text_area(
    "Tu respuesta",
    height=120,
    placeholder="Escribe tu respuesta aqui...",
)

if st.button("Evaluar respuesta", type="primary"):
    respuesta_correcta = get_answer_for_question(pregunta_seleccionada)
    if not respuesta_correcta:
        st.error("No se encontro la respuesta correcta.")
    else:
        estado, similitud = evaluar_respuesta(respuesta_usuario, respuesta_correcta)
        if estado == "correcto":
            st.success(f"**Estado:** {estado} · **Similitud:** {similitud:.3f}")
        elif estado == "incompleto":
            st.warning(f"**Estado:** {estado} · **Similitud:** {similitud:.3f}")
        else:
            st.error(f"**Estado:** {estado} · **Similitud:** {similitud:.3f}")
        st.markdown(f"**Respuesta correcta:** {respuesta_correcta}")
