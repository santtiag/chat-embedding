import streamlit as st

from db.repository import get_top_questions
from startup import inicializar_app
from ui import aplicar_estilos, encabezado

inicializar_app()
aplicar_estilos()

encabezado("Top 10", "Preguntas mas consultadas por los usuarios")

top = get_top_questions(10)

if not top:
    st.info("Aun no hay consultas registradas.")
else:
    datos = [
        {"#": i + 1, "Pregunta": item.pregunta, "Consultas": item.count}
        for i, item in enumerate(top)
    ]
    st.dataframe(datos, use_container_width=True, hide_index=True)
