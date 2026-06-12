import streamlit as st

from db.repository import get_topics_with_stats
from startup import inicializar_app
from ui import aplicar_estilos, encabezado

inicializar_app()
aplicar_estilos()

encabezado("Explorar temas", "Revisa los temas disponibles y ejemplos de preguntas")

temas = get_topics_with_stats()

if not temas:
    st.warning("No hay temas cargados en la base de conocimiento.")
else:
    for tema in temas:
        with st.expander(f"{tema.nombre} — {tema.cantidad} preguntas"):
            st.markdown(f"**Archivo:** `{tema.archivo}`")
            st.markdown(f"**Cantidad de preguntas:** {tema.cantidad}")
            if tema.ejemplos:
                st.markdown("**Ejemplos:**")
                for ejemplo in tema.ejemplos:
                    st.markdown(f"- {ejemplo}")
            else:
                st.caption("Sin ejemplos disponibles.")
