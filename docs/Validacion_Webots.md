# Validación técnica en Webots R2025a

Fecha: 27 de junio de 2026. Entorno: Webots R2025a, SUMO 1.27.1, macOS.

## Evidencia obtenida

| Ruta | Comando | Evidencia | Resultado |
|---|---:|---|---|
| Recto | 0 | Autobús a 11.74 m; Recognition, LiDAR, radar, giroscopio y laterales activos | Evasión completa; llegadas a silos `GPS=(-188.08,235.10)` y `(-188.03,235.40)` |
| Derecha | 2 | Peatón reconocido a 14.25 m y confirmado por LiDAR a 11.93 m | `FRENO_PEATON` a 0 km/h; llegadas limpias `GPS=(23.96,-89.60)` y `(28.97,-65.41)` |
| Izquierda | 1 | Giro CIL y estabilización del corredor con todos los sensores y SUMO activos | Dos llegadas limpias: `GPS=(35.04,25.75)` y `(35.04,28.37)` |

Los clips reproducibles de recorrido completo se generaron localmente como
`media/route_straight_camera.mp4`, `media/route_right_camera.mp4` y
`media/route_left_camera.mp4`; los videos temporales se excluyen del repositorio
para no inflarlo. Los logs conservan las transiciones y la línea `RUTA COMPLETA`.

## Alcance de esta validación

Se completaron dos ejecuciones limpias por ruta, por carril derecho, sin colisión
ni U-turn. La validación encontró y corrigió una falsa coincidencia entre
`BusSimple` y el mobiliario `bus stop`; una prueba unitaria evita la regresión.
Queda pendiente únicamente editar el video con la participación de los cuatro
integrantes y publicar su URL real de YouTube.
