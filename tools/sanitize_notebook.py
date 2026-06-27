#!/usr/bin/env python3
"""Retira rutas locales de las salidas sin alterar celdas ni resultados."""

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NOTEBOOK = ROOT / "Proyecto_Final_Equipo19.ipynb"
PUBLIC_ROOT = "/content/proyecto-final-cil-equipo19"


def replace(value):
    if isinstance(value, str):
        return value.replace(str(ROOT), PUBLIC_ROOT)
    if isinstance(value, list):
        return [replace(item) for item in value]
    if isinstance(value, dict):
        return {key: replace(item) for key, item in value.items()}
    return value


data = json.loads(NOTEBOOK.read_text(encoding="utf-8"))
data = replace(data)
NOTEBOOK.write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
print(NOTEBOOK)
