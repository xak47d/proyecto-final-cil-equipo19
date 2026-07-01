# Proyecto Final - Navegacion Autonoma - Equipo 19

Solucion de Conditional Imitation Learning (CIL) en Webots R2025a para los
comandos `STRAIGHT`, `LEFT` y `RIGHT`, integrada con frenado ante peatones,
evasion de autobuses estacionados y control de distancia mediante radar.

## Estructura

- `Proyecto_Final_Equipo19.ipynb`: entrenamiento reproducible en Google Colab.
- `dataset/`: 6,129 imagenes originales y CSV normalizado de tres comandos.
- `controllers/`: captura en World 1 y conduccion autonoma en World 2.
- `worlds/`: mundos originales y tres presets de evaluacion.
- `docs/`: reporte final, matriz de cumplimiento y figuras.
- `run_final_project.sh`: lanzador reproducible para macOS.

## Entrenamiento en Colab

La primera celda del notebook clona este repositorio. El notebook divide los
datos originales antes de aplicar aumentos para impedir fuga entre entrenamiento
y validacion, y exporta `cil_model.h5` y `model_metadata.json`.

## Ejecucion en Webots

```bash
./run_final_project.sh --setup
./run_final_project.sh --route straight
./run_final_project.sh --route right
./run_final_project.sh --route left
```

Teclas durante la simulacion: `W` recto, `A` izquierda y `D` derecha.
Agrega `--record` para generar un MP4 H.264 de 1920 x 1080 px a 30 fps. La
camara global mantiene el vehiculo en cuadro sin rotar con cada correccion de
direccion; `ffmpeg` se usa para la codificacion final.

## Rutas de evidencia

1. Torres residenciales del noreste a silos: recto, distancia y evasion.
2. Subway norte a iglesia: derecha y frenado ante peaton.
3. Parque infantil a Subway norte: izquierda.

El video final debe ser menor de seis minutos y debe incluir la participacion
de los cuatro integrantes. El guion se encuentra en `docs/Guion_Video_Equipo19.md`.

## Resultados finales

- 6,129 muestras originales, sin imagenes faltantes ni referencias huerfanas.
- 12,956 muestras tras aumento; la separacion por `source_id` evita fuga.
- MAE de validacion global: `0.0220 rad` (objetivo: `<= 0.05 rad`).
- Diecisiete pruebas automatizadas cubren integridad, one-hot, preprocesamiento,
  limites de direccion, umbrales de distancia, histéresis, presets, corredor
  legal de rebase y permanencia en el centro de carril `y=236.40`.
- Webots R2025a + SUMO 1.27.1: dos recorridos limpios por ruta, frenado ante
  peaton, control de distancia y evasion completa sin invadir el sentido
  opuesto; la ruta recta vuelve a `y=236.40` y conserva ese carril hasta el
  destino. Los resultados se documentan en
  `docs/Validacion_Webots.md`.

Video final publicado en YouTube: https://youtu.be/YObQTAm8_VM
