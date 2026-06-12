# Chatbot Educativo — Streamlit + Neon

Chatbot de lookup semantico (no generativo) que responde preguntas comparando consultas contra una base de conocimiento usando **Sentence Transformers** y PostgreSQL en la nube (**Neon**).

## Requisitos

- [uv](https://docs.astral.sh/uv/) (recomendado) o Python 3.11–3.13 con pip
- Cuenta en [Neon](https://neon.tech) (recomendado) u otra base PostgreSQL
- ~500 MB de espacio para el modelo de embeddings

## Instalacion local (recomendado: uv)

**uv** crea un entorno virtual aislado en `.venv/` sin instalar paquetes en tu sistema.

```bash
cd chatbot_streamlit
cp .env.example .env
# Edita .env con tu DATABASE_URL de Neon

# Si no tienes uv:
# curl -LsSf https://astral.sh/uv/install.sh | sh

uv sync
uv run streamlit run app.py
```

Atajo con script:

```bash
./run.sh
```

### Alternativa con pip (venv manual)

```bash
cd chatbot_streamlit
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
```

Edita `.env` con tu `DATABASE_URL`.

## Configurar Neon

1. Crea una cuenta en [Neon](https://console.neon.tech)
2. Crea un proyecto y copia la **connection string** (formato pooler recomendado)
3. Pégala en `.env` **tal cual** — no hace falta cambiar `postgresql://` a mano:

```bash
DATABASE_URL=postgresql://neondb_owner:TU_PASSWORD@ep-xxxx-pooler.eastus2.azure.neon.tech/neondb?sslmode=require&channel_binding=require
```

La app convierte automáticamente a `postgresql+psycopg2://...` y ajusta `channel_binding` para compatibilidad local.

4. Guarda `.env` y ejecuta `uv sync` si aún no lo hiciste

Al primer arranque, la app crea las tablas automaticamente y carga los archivos de `data/`.

## Alternativas a Neon

La misma `DATABASE_URL` funciona con cualquier PostgreSQL compatible:

| Servicio | Notas |
|----------|-------|
| [Supabase](https://supabase.com) | PostgreSQL gestionado, tier gratuito |
| [ElephantSQL](https://www.elephantsql.com) | Tier gratuito limitado |
| PostgreSQL local | `postgresql+psycopg2://usuario:clave@localhost:5432/chatbot` |

## Ejecutar

```bash
uv run streamlit run app.py
# o: ./run.sh
```

La primera carga del modelo transformer puede tardar **30–60 segundos**. Veras un spinner al iniciar.

**Nota:** si ves error de conexion a la base de datos, revisa que `.env` tenga una `DATABASE_URL` valida de Neon (no basta con copiar `.env.example`).

## Solucion de problemas

| Error | Causa probable | Solucion |
|-------|----------------|----------|
| `Field required DATABASE_URL` | Falta archivo `.env` | `cp .env.example .env` y pega tu URL de Neon |
| `connection refused` / `127.0.0.1:5433` | Variable `DATABASE_URL` exportada en la shell pisa el `.env` | Usa `./run.sh` o `unset DATABASE_URL` antes de arrancar |
| `DATABASE_URL sigue siendo el ejemplo` | `.env` tiene el placeholder `ep-xxxx` | Pega la URL real desde [console.neon.tech](https://console.neon.tech) |
| Paquetes no encontrados | Entorno viejo o sin instalar | Usa `uv sync` (no instales con pip en el sistema) |
| Conflicto `venv` vs `.venv` | Habia un venv manual anterior | Borra la carpeta `venv/` y usa solo `uv sync` |

El entorno aislado vive en `.venv/` dentro del proyecto. Nada se instala en Python del sistema.

## Paginas

| Pagina | Descripcion |
|--------|-------------|
| Chat | Conversacion con pipeline matematica → embedding → fallback |
| Explorar | Temas, cantidad de preguntas y ejemplos |
| Quiz | Pregunta aleatoria con evaluacion difflib |
| Aprender | Aprendizaje guiado por tema |
| Dashboard | Metricas de consultas por tipo |
| Top | 10 preguntas mas consultadas |
| Agregar | Anadir conocimiento en caliente |

## Despliegue en Streamlit Cloud

1. Sube este repositorio a GitHub
2. Ve a [share.streamlit.io](https://share.streamlit.io) y crea una nueva app
3. Selecciona el repositorio y establece `app.py` como entrypoint
4. En **Secrets**, configura:

```toml
DATABASE_URL = "postgresql://USER:PASSWORD@ep-xxxx-pooler.region.aws.neon.tech/neondb?sslmode=require"
EMBEDDING_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
EMBEDDING_THRESHOLD = "0.35"
```

5. Despliega. La primera carga del modelo puede ser lenta en el tier gratuito.

**Importante:** no subas `.env` con credenciales reales al repositorio.

## Variables de entorno

| Variable | Default | Descripcion |
|----------|---------|-------------|
| `DATABASE_URL` | (requerida) | URL PostgreSQL con driver `psycopg2` |
| `EMBEDDING_MODEL` | `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` | Modelo de embeddings |
| `EMBEDDING_THRESHOLD` | `0.35` | Umbral minimo de similitud coseno |

## Checklist de prueba manual

- [ ] `streamlit run app.py` arranca sin errores con `DATABASE_URL` de Neon
- [ ] Se crean tablas y se seedean los 5 archivos `.txt` en primer arranque
- [ ] Chat responde matematica: `"cuanto es 5 mas 3"` → `"El resultado es: 8.0"`
- [ ] Chat responde embedding: `"que es el machine learning"`
- [ ] Chat devuelve fallback: `"cual es la capital de marte"`
- [ ] Cada consulta se registra en `query_logs`
- [ ] Feedback se guarda en `feedback`
- [ ] Quiz evalua respuestas (correcto / incompleto / incorrecto)
- [ ] Aprender filtra por tema y evalua respuestas
- [ ] Explorar lista temas con ejemplos
- [ ] Dashboard muestra conteos y porcentajes
- [ ] Top muestra las 10 preguntas mas consultadas
- [ ] Agregar inserta en DB y funciona en chat sin reiniciar

## Estructura del proyecto

```
chatbot_streamlit/
├── app.py              # Entrypoint y navegacion
├── config.py           # Configuracion con pydantic-settings
├── startup.py          # Inicializacion cacheada de DB y embeddings
├── data/               # Archivos .txt para seed inicial
├── db/                 # Modelos SQLAlchemy y repositorio
├── services/           # Motores matematico, embeddings y chat
└── pages/              # 7 paginas Streamlit
```

## Licencia

Proyecto educativo — electiva Ciencia de la Computacion.
