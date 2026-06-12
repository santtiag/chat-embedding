import streamlit as st

st.set_page_config(
    page_title="Chatbot de Aprendizaje",
    layout="wide",
    initial_sidebar_state="expanded",
)

from config import obtener_error_configuracion
from ui import aplicar_estilos

aplicar_estilos()

error_config = obtener_error_configuracion()
if error_config:
    st.error("Falta configurar la base de datos")
    st.markdown(
        """
        ### Pasos

        1. Abre el archivo **`.env`** en la carpeta del proyecto.
        2. Ve a [console.neon.tech](https://console.neon.tech) → tu proyecto → **Connection string**.
        3. Copia la URL completa (formato `postgresql://...@ep-....pooler....neon.tech/neondb?...`).
        4. Pégala en `.env`:

        ```
        DATABASE_URL=postgresql://neondb_owner:TU_PASSWORD@ep-tu-proyecto-pooler.region.aws.neon.tech/neondb?sslmode=require
        ```

        5. Guarda el archivo y reinicia con `./run.sh` o `uv run streamlit run app.py`.

        **Forma mas facil (recomendada):**

        ```bash
        uv run python setup_env.py
        ```

        Pega la URL completa con **Ctrl+Shift+V** cuando te lo pida. Luego:

        ```bash
        uv run python setup_env.py --test
        ./run.sh
        ```
        """
    )
    st.code(error_config, language="text")
    st.stop()

with st.sidebar:
    st.title("Chatbot Educativo")
    st.caption("Plataforma de aprendizaje con busqueda semantica")
    st.divider()

try:
    with st.spinner("Cargando modelo y base de conocimiento..."):
        from startup import inicializar_app

        total_pares = inicializar_app()
    st.sidebar.success(f"Base de conocimiento: {total_pares} pares")
except Exception as exc:
    detalle = str(exc)
    if "password authentication failed" in detalle.lower():
        st.error(
            "La contraseña de Neon en `.env` es incorrecta o está incompleta.\n\n"
            "Ve a [console.neon.tech](https://console.neon.tech) → **Connection string** → "
            "botón **Copy** y vuelve a pegar la URL **completa**:\n\n"
            "```bash\nuv run python setup_env.py 'postgresql://...'\n```"
        )
    else:
        st.error(f"No se pudo conectar a la base de datos.\n\n**Detalle:** {exc}")
    st.stop()

paginas = [
    st.Page("pages/1_Chat.py", title="Chat", icon=":material/chat:"),
    st.Page("pages/2_Explorar.py", title="Explorar", icon=":material/menu_book:"),
    st.Page("pages/3_Quiz.py", title="Quiz", icon=":material/quiz:"),
    st.Page("pages/4_Aprender.py", title="Aprender", icon=":material/school:"),
    st.Page("pages/5_Dashboard.py", title="Dashboard", icon=":material/analytics:"),
    st.Page("pages/6_Top.py", title="Top", icon=":material/leaderboard:"),
    st.Page("pages/7_Agregar.py", title="Agregar", icon=":material/add:"),
]

navegacion = st.navigation(paginas)
navegacion.run()
