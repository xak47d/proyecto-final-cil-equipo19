# Validación técnica en Webots R2025a

Fecha de ejecución: 27 de junio de 2026. Revalidación de videos: 29 de junio
de 2026. Entorno: Webots R2025a, SUMO 1.27.1, macOS.

## Evidencia obtenida

| Ruta | Comando | Evidencia | Resultado |
|---|---:|---|---|
| Recto | 0 | Autobús a 11.74 m; Recognition, LiDAR, radar, giroscopio y laterales activos | Evasión completa; llegadas a silos `GPS=(-188.08,235.10)` y `(-188.03,235.40)` |
| Derecha | 2 | Peatón reconocido a 14.25 m y confirmado por LiDAR a 11.93 m | `FRENO_PEATON` a 0 km/h; llegadas limpias `GPS=(23.96,-89.60)` y `(28.97,-65.41)` |
| Izquierda | 1 | Giro CIL y estabilización del corredor con todos los sensores y SUMO activos | Dos llegadas limpias: `GPS=(35.04,25.75)` y `(35.04,28.37)` |

Los clips reproducibles de recorrido completo se generaron localmente como
`media/route_straight_camera.mp4`, `media/route_right_camera.mp4` y
`media/route_left_camera.mp4`. Las copias listas para entrega se guardaron como
`media/entrega/Equipo19_Ruta_Recta.mp4`,
`media/entrega/Equipo19_Ruta_Derecha.mp4` y
`media/entrega/Equipo19_Ruta_Izquierda.mp4`. Los videos se excluyen del
repositorio para no inflarlo; los logs conservan las transiciones y la línea
`RUTA COMPLETA`.

## Validación de los videos guardados

| Ruta | Archivo de entrega | Duración | Evidencia del recorrido | Resultado |
|---|---|---:|---|---|
| Recta | `Equipo19_Ruta_Recta.mp4` | 46.656 s | Evasión del autobús, seguimiento de pared, recuperación, reincorporación, tráfico y llegada | Cumple |
| Derecha | `Equipo19_Ruta_Derecha.mp4` | 31.824 s | Freno ante peatón, reanudación, giro derecho y llegada | Cumple |
| Izquierda | `Equipo19_Ruta_Izquierda.mp4` | 27.056 s | Giro izquierdo, estabilización en el corredor y llegada | Cumple |

Los tres MP4 son MPEG-4 de 320 x 160 px a 62.5 fps. `ffmpeg` decodificó cada
archivo completo sin errores. Se inspeccionó visualmente un cuadro por segundo,
además del inicio y el final en QuickTime Player: no se observan colisiones,
salida del recorrido ni U-turn. La duración acumulada es 1:45.536, por debajo
del máximo de seis minutos para la posterior edición del video final.

SHA-256 de las copias de entrega:

- Recta: `c4d69405009dc3c27d530daccfc3f70f94a0ab3a85fd09c95ea6c958e7163bb5`.
- Derecha: `185c613b22f81e3925c125b09e7d11acde86b692c25331d95cc92d6dad9141cd`.
- Izquierda: `006ae8e1d8da82db61fe03cd1c1e19c6c96c7b0aaf6d0780a20e9ad11da5642e`.

## Alcance de esta validación

Se completaron dos ejecuciones limpias por ruta, por carril derecho, sin colisión
ni U-turn. La validación encontró y corrigió una falsa coincidencia entre
`BusSimple` y el mobiliario `bus stop`; una prueba unitaria evita la regresión.
Las doce pruebas automatizadas volvieron a pasar y los tres mundos conservan
`maxVehicles 30`, Camera Recognition, LiDAR, radar, giroscopio y los tres
sensores laterales. Queda pendiente únicamente editar el video con la
participación de los cuatro integrantes y publicar su URL real de YouTube.
