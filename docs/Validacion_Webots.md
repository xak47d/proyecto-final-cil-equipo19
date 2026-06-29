# Validación técnica en Webots R2025a

Fecha de ejecución: 27 de junio de 2026. Revalidación de videos: 29 de junio
de 2026. Entorno: Webots R2025a, SUMO 1.27.1, macOS.

## Evidencia obtenida

| Ruta | Comando | Evidencia | Resultado |
|---|---:|---|---|
| Recto | 0 | Autobús a 11.74 m; Recognition, LiDAR, radar, giroscopio y laterales activos | Evasión completa y llegada a silos `GPS=(-188.01,235.51)` |
| Derecha | 2 | Peatón reconocido y confirmado por LiDAR dentro del umbral de 15 m | `FRENO_PEATON` a 0 km/h; aproximación centrada, giro contenido y llegada `GPS=(28.99,-67.09)` |
| Izquierda | 1 | Aproximación centrada, giro asistido y estabilización del corredor | Giro dentro de la intersección y llegada `GPS=(35.01,47.85)` |

Los clips reproducibles de recorrido completo se generaron localmente como
`media/route_straight_global_1080p.mp4`,
`media/route_right_global_1080p.mp4` y
`media/route_left_global_1080p.mp4`. Las copias listas para entrega se guardaron como
`media/entrega/Equipo19_Ruta_Recta.mp4`,
`media/entrega/Equipo19_Ruta_Derecha.mp4` y
`media/entrega/Equipo19_Ruta_Izquierda.mp4`. Los videos se excluyen del
repositorio para no inflarlo; los logs conservan las transiciones y la línea
`RUTA COMPLETA`.

## Validación de los videos guardados

| Ruta | Archivo de entrega | Duración | Evidencia del recorrido | Resultado |
|---|---|---:|---|---|
| Recta | `Equipo19_Ruta_Recta.mp4` | 45.033 s | Evasión del autobús, seguimiento de pared, recuperación, reincorporación, tráfico y llegada | Cumple |
| Derecha | `Equipo19_Ruta_Derecha.mp4` | 32.567 s | Freno ante peatón, reanudación, aproximación centrada, giro derecho y llegada | Cumple |
| Izquierda | `Equipo19_Ruta_Izquierda.mp4` | 30.967 s | Aproximación centrada, giro izquierdo, corredor estable y llegada | Cumple |

Los tres MP4 usan H.264, resolución nativa de 1920 x 1080 px y 30 fps.
Una cámara de evidencia independiente sigue la posición del vehículo en ejes
globales, sin rotar con las correcciones de dirección. El encuadre se validó
mediante hojas de contacto de cada recorrido: el vehículo permanece visible y
se conserva contexto de carriles, peatones y tráfico. `ffmpeg` decodificó cada
archivo completo sin errores. No se observan colisiones, salida del recorrido
ni U-turn. La duración acumulada es 1:48.567, por debajo del máximo de seis
minutos para la posterior edición del video final.

SHA-256 de las copias de entrega:

- Recta: `38e8b70d03f4eccc29e6eb35a92e7971898d4d42cfddfc4f39a45af1da37ecec`.
- Derecha: `eb6241da46236d3420b5b184bf0b6329becb20b84e2e86fd1ac73a256be0ded1`.
- Izquierda: `ddfa91a27677af6be70e8e4f7974c4d900f4fa94ed1b239cee75b00439edf0b2`.

## Alcance de esta validación

Las ejecuciones finales terminaron con `RUTA COMPLETA`, por carril derecho, sin
colisión ni U-turn. La revalidación corrigió la deriva previa al cruce mediante
centrado de carril, afinó los destinos reales y eliminó la rotación absurda de
la cámara global. También conserva la corrección que distingue `BusSimple` del
mobiliario `bus stop`. Las doce pruebas automatizadas volvieron a pasar y los tres mundos conservan
`maxVehicles 30`, Camera Recognition, LiDAR, radar, giroscopio y los tres
sensores laterales. Queda pendiente únicamente editar el video con la
participación de los cuatro integrantes y publicar su URL real de YouTube.
