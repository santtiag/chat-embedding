import streamlit as st

_ESTILOS = """
<style>
:root {
    --color-borde: #e2e8f0;
    --color-tenue: #64748b;
}

section.main > div.block-container {
    padding-top: 2.5rem;
    max-width: 1100px;
}

h1, h2, h3 {
    font-weight: 650;
    letter-spacing: -0.01em;
    color: #0f172a;
}

.app-encabezado {
    margin-bottom: 1.75rem;
    padding-bottom: 1rem;
    border-bottom: 1px solid var(--color-borde);
}

.app-encabezado .titulo {
    font-size: 1.65rem;
    font-weight: 650;
    letter-spacing: -0.02em;
    color: #0f172a;
}

.app-encabezado .subtitulo {
    margin-top: 0.25rem;
    font-size: 0.95rem;
    color: var(--color-tenue);
}

.app-etiqueta {
    display: inline-block;
    margin-top: 0.35rem;
    padding: 0.15rem 0.6rem;
    font-size: 0.78rem;
    font-weight: 500;
    border-radius: 999px;
    border: 1px solid var(--color-borde);
    background: #f8fafc;
    color: var(--color-tenue);
}

div[data-testid="stMetric"] {
    border: 1px solid var(--color-borde);
    border-radius: 10px;
    padding: 1rem 1.1rem;
    background: #ffffff;
}

.stButton > button {
    border-radius: 8px;
    font-weight: 550;
}

div[data-testid="stExpander"] {
    border-radius: 10px;
    border: 1px solid var(--color-borde);
}
</style>
"""


def aplicar_estilos() -> None:
    """Inyecta los estilos globales de la aplicacion."""
    st.markdown(_ESTILOS, unsafe_allow_html=True)


def encabezado(titulo: str, subtitulo: str | None = None) -> None:
    """Renderiza un encabezado de pagina consistente y sin emojis."""
    subtitulo_html = (
        f'<div class="subtitulo">{subtitulo}</div>' if subtitulo else ""
    )
    st.markdown(
        f'<div class="app-encabezado">'
        f'<div class="titulo">{titulo}</div>'
        f"{subtitulo_html}"
        f"</div>",
        unsafe_allow_html=True,
    )


def etiqueta(texto: str) -> None:
    """Renderiza una etiqueta tipo badge neutra."""
    st.markdown(f'<span class="app-etiqueta">{texto}</span>', unsafe_allow_html=True)
