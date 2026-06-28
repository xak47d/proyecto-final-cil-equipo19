#!/bin/zsh
# Lanzador reproducible de World 2 y el controlador externo CIL en macOS.

set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
ROUTE="straight"
SETUP=0
RECORD=0
FAST=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --route) shift; ROUTE="$1" ;;
    --setup) SETUP=1 ;;
    --record) RECORD=1 ;;
    --fast) FAST=1 ;;
    -h|--help)
      echo "Uso: $0 [--setup] [--route straight|right|left] [--record] [--fast]"
      exit 0
      ;;
    *) echo "Argumento desconocido: $1"; exit 2 ;;
  esac
  shift
done

case "$ROUTE" in
  straight) INITIAL_COMMAND=0 ;;
  left) INITIAL_COMMAND=1 ;;
  right) INITIAL_COMMAND=2 ;;
  *) echo "Ruta invalida: $ROUTE"; exit 2 ;;
esac

WEBOTS_HOME="${WEBOTS_HOME:-/Applications/Webots.app}"
if [[ ! -d "$WEBOTS_HOME" ]]; then
  echo "No se encontro Webots. Define WEBOTS_HOME."
  exit 1
fi
export WEBOTS_HOME

if command -v sumo >/dev/null 2>&1; then
  SUMO_PREFIX="$(brew --prefix sumo 2>/dev/null || true)"
  if [[ -n "$SUMO_PREFIX" && -d "$SUMO_PREFIX/share/sumo" ]]; then
    export SUMO_HOME="$SUMO_PREFIX/share/sumo"
  fi
fi

VENV="$ROOT/.venv-final"
if [[ $SETUP -eq 1 || ! -x "$VENV/bin/python" ]]; then
  command -v uv >/dev/null || { echo "Se requiere uv para crear Python 3.12"; exit 1; }
  uv venv --python 3.12 "$VENV"
  uv pip install --python "$VENV/bin/python" -r "$ROOT/requirements_webots.txt"
  if [[ $SETUP -eq 1 ]]; then
    echo "Entorno listo: $VENV"
    exit 0
  fi
fi

if [[ -z "${SUMO_HOME:-}" ]]; then
  SUMO_HOME="$($VENV/bin/python -c 'import sumo; print(sumo.SUMO_HOME)' 2>/dev/null || true)"
  if [[ -n "$SUMO_HOME" && -x "$SUMO_HOME/bin/sumo" ]]; then
    export SUMO_HOME
    export PATH="$SUMO_HOME/bin:$PATH"
  else
    echo "No se encontro SUMO. Ejecuta $0 --setup."
    exit 1
  fi
fi

WORLD="$ROOT/worlds/city_traffic_2025_02_route_${ROUTE}.wbt"
CONTROLLER="$ROOT/controllers/cil_autonomous_driver/cil_autonomous_driver.py"
"$VENV/bin/python" "$ROOT/tools/create_route_worlds.py" >/dev/null
[[ -f "$WORLD" ]] || { echo "No existe $WORLD"; exit 1; }

pick_free_port() {
  python3 - <<'PY'
import socket
s = socket.socket()
s.bind(("127.0.0.1", 0))
print(s.getsockname()[1])
s.close()
PY
}

PORT="${WEBOTS_PORT:-$(pick_free_port)}"
MODE="realtime"
WEBOTS_EXTRA=()
if [[ $FAST -eq 1 ]]; then
  MODE="fast"
  WEBOTS_EXTRA+=(--no-rendering)
  export WEBOTS_FORCE_FAST=1
fi

export PYTHONPATH="$WEBOTS_HOME/Contents/lib/controller/python"
export WEBOTS_PYTHON_EXECUTABLE="$VENV/bin/python"
export WEBOTS_CONTROLLER_URL="tcp://localhost:${PORT}/vehicle"
export CIL_INITIAL_COMMAND="$INITIAL_COMMAND"
export CIL_ROUTE="$ROUTE"

mkdir -p "$ROOT/media"
LOG="$ROOT/media/route_${ROUTE}.log"
if [[ $RECORD -eq 1 ]]; then
  export CIL_RECORD_PATH="$ROOT/media/route_${ROUTE}_camera.mp4"
  export CIL_MAX_SECONDS="${CIL_MAX_SECONDS:-90}"
fi

echo "Webots: $WORLD"
echo "Ruta: $ROUTE | comando: $INITIAL_COMMAND | puerto: $PORT"
cd "$ROOT"
CAFFEINATE_PID=""
if command -v caffeinate >/dev/null 2>&1; then
  caffeinate -dimsu &
  CAFFEINATE_PID=$!
fi
"$WEBOTS_HOME/Contents/MacOS/webots" \
  --batch "${WEBOTS_EXTRA[@]}" --port="$PORT" --mode="$MODE" --stdout --stderr "$WORLD" &
WEBOTS_PID=$!

cleanup() {
  if kill -0 "$WEBOTS_PID" 2>/dev/null; then
    kill "$WEBOTS_PID" 2>/dev/null || true
  fi
  if [[ -n "$CAFFEINATE_PID" ]] && kill -0 "$CAFFEINATE_PID" 2>/dev/null; then
    kill "$CAFFEINATE_PID" 2>/dev/null || true
  fi
}
trap cleanup EXIT INT TERM

sleep 5
cd "$(dirname "$CONTROLLER")"
"$VENV/bin/python" -u "$CONTROLLER" 2>&1 | tee "$LOG"
