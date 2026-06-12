#!/usr/bin/env bash
# Ejecuta la app con uv (entorno aislado, sin instalar en el sistema).
set -euo pipefail
cd "$(dirname "$0")"

if [[ ! -f .env ]]; then
  echo "Copia .env.example a .env y configura DATABASE_URL (Neon)."
  echo "  cp .env.example .env"
  echo "O pega tu URL de Neon con:"
  echo "  uv run python setup_env.py 'postgresql://...'"
  exit 1
fi

if ! uv run python -c "from config import obtener_error_configuracion; import sys; sys.exit(1 if obtener_error_configuracion() else 0)" 2>/dev/null; then
  echo ""
  echo "DATABASE_URL no configurada o incompleta."
  echo "Ejecuta el asistente interactivo (pega la URL con Ctrl+Shift+V):"
  echo "  uv run python setup_env.py"
  echo ""
  exit 1
fi

if ! command -v uv >/dev/null 2>&1; then
  echo "Instala uv: curl -LsSf https://astral.sh/uv/install.sh | sh"
  exit 1
fi

# Evitar conflicto con un venv manual antiguo (venv/ vs .venv/)
unset VIRTUAL_ENV
# Evitar que un DATABASE_URL exportado en la shell pise el .env del proyecto
unset DATABASE_URL

uv sync
exec uv run streamlit run app.py "$@"
