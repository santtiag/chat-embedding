import streamlit as st

from db.repository import get_topics_with_stats, insert_knowledge_pair
from services import embedding_engine
from startup import inicializar_app
from ui import aplicar_estilos, encabezado

inicializar_app()
aplicar_estilos()

encabezado("Agregar conocimiento", "Anade nuevos pares de pregunta y respuesta")

temas = get_topics_with_stats()
slugs_existentes = [t.archivo.replace(".txt", "") for t in temas]

with st.form("form_agregar"):
    usar_nuevo = st.checkbox("Crear tema nuevo")
    if usar_nuevo:
        tema = st.text_input("Nombre del tema nuevo (slug)", placeholder="ej: biologia")
    else:
        tema = st.selectbox("Tema", slugs_existentes if slugs_existentes else ["general"])

    pregunta = st.text_input("Pregunta")
    respuesta = st.text_area("Respuesta", height=120)
    enviar = st.form_submit_button("Agregar", type="primary")

if enviar:
    if not pregunta.strip() or not respuesta.strip() or not tema.strip():
        st.error("Completa todos los campos.")
    else:
        slug = tema.strip().lower().replace(".txt", "")
        insert_knowledge_pair(slug, pregunta.strip(), respuesta.strip())
        embedding_engine.add_knowledge(pregunta.strip(), respuesta.strip())
        st.success(
            f"Conocimiento agregado al tema **{slug}**. "
            "Ya esta disponible en el chat sin reiniciar."
        )
