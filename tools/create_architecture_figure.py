#!/usr/bin/env python3
"""Genera una figura de arquitectura a partir del HDF5 entrenado."""

from pathlib import Path
import matplotlib.pyplot as plt
import tensorflow as tf


ROOT = Path(__file__).resolve().parents[1]
MODEL = ROOT / "controllers" / "cil_autonomous_driver" / "cil_model.h5"
OUTPUT = ROOT / "docs" / "figures" / "model_architecture.png"

model = tf.keras.models.load_model(MODEL, compile=False)
layers = []
for layer in model.layers:
    try:
        shape = str(layer.output.shape)
    except AttributeError:
        shape = "multiple"
    layers.append((layer.name, layer.__class__.__name__, shape, layer.count_params()))

fig, ax = plt.subplots(figsize=(12, 8.4))
ax.axis("off")
ax.set_xlim(0, 12)
ax.set_ylim(0, len(layers) + 2)
colors = {
    "InputLayer": "#DCE6F1",
    "Conv2D": "#9DC3E6",
    "Dense": "#A9D18E",
    "Concatenate": "#FFD966",
    "Flatten": "#F4B183",
}
for i, (name, kind, shape, params) in enumerate(layers):
    y = len(layers) - i
    color = colors.get(kind, "#E7E6E6")
    ax.add_patch(plt.Rectangle((0.7, y - 0.34), 10.6, 0.68, facecolor=color, edgecolor="#44546A"))
    ax.text(1.0, y, name, va="center", fontsize=9, fontweight="bold")
    ax.text(4.1, y, kind, va="center", fontsize=9)
    ax.text(6.3, y, shape, va="center", fontsize=8, family="monospace")
    ax.text(10.7, y, f"{params:,}", va="center", ha="right", fontsize=8)
ax.text(0.7, len(layers) + 1.2, "CNN condicionada por comando (modelo HDF5 real)", fontsize=15, fontweight="bold", color="#1F4E79")
ax.text(10.7, len(layers) + 0.65, f"Parametros totales: {model.count_params():,}", ha="right", fontsize=10)
ax.text(1.0, len(layers) + 0.65, "Capa", fontsize=9, fontweight="bold")
ax.text(4.1, len(layers) + 0.65, "Tipo", fontsize=9, fontweight="bold")
ax.text(6.3, len(layers) + 0.65, "Salida", fontsize=9, fontweight="bold")
ax.text(10.7, len(layers) + 0.65, "Parametros", ha="right", fontsize=9, fontweight="bold")
fig.tight_layout()
OUTPUT.parent.mkdir(parents=True, exist_ok=True)
fig.savefig(OUTPUT, dpi=180, bbox_inches="tight")
print(OUTPUT)
