import streamlit as st

from db.repository import get_dashboard_metrics
from startup import inicializar_app
from ui import aplicar_estilos, encabezado

inicializar_app()
aplicar_estilos()

encabezado("Dashboard", "Metricas de consultas por tipo de respuesta")

datos = get_dashboard_metrics()

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total consultas", datos.total)
col2.metric("Embedding", datos.metricas.get("embedding", 0))
col3.metric("Matematica", datos.metricas.get("matematica", 0))
col4.metric("Sin respuesta", datos.metricas.get("ninguna", 0))

st.subheader("Porcentajes por tipo")
if datos.total > 0:
    filas = [
        {
            "tipo": tipo,
            "conteo": datos.metricas[tipo],
            "porcentaje": datos.porcentajes[tipo],
        }
        for tipo in datos.metricas
    ]
    st.bar_chart({fila["tipo"]: fila["conteo"] for fila in filas})

    for fila in filas:
        st.write(
            f"**{fila['tipo']}:** {fila['conteo']} consultas "
            f"({fila['porcentaje']}%)"
        )
else:
    st.info("Aun no hay consultas registradas. Usa el chat para generar metricas.")
