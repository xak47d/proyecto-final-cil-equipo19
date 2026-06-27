# Validación técnica en Webots R2025a

Fecha: 27 de junio de 2026. Entorno: Webots R2025a, SUMO 1.27.1, macOS.

## Evidencia obtenida

| Ruta | Comando | Evidencia | Resultado |
|---|---:|---|---|
| Recto | 0 | Cámara, Recognition, LiDAR, radar y giroscopio activos; autobús a 11.74 m | Se activó `EVASION_SEPARACION` a 4.62 m de LiDAR y 12 km/h |
| Derecha | 2 | Peatón reconocido a 14.25 m y confirmado por LiDAR a 11.93 m | Se activó `FRENO_PEATON`; velocidad objetivo 0 km/h |
| Izquierda | 1 | Inferencia CIL, cámara, LiDAR y SUMO activos durante 2.0 s | Control CIL ejecutado a 22 km/h sin error del controlador |

Los clips técnicos reproducibles se generaron localmente como
`media/route_straight_camera.mp4`, `media/route_right_camera.mp4` y
`media/route_left_camera.mp4`. Sus duraciones verificadas con `ffprobe` son
1.008 s, 1.008 s y 2.000 s, respectivamente.

## Alcance de esta validación

Estas pruebas confirman integración, dispositivos, comandos y transiciones de
seguridad. No sustituyen la aceptación final supervisada de las tres rutas de
principio a fin. Antes de entregar el video, el equipo debe realizar dos tomas
limpias por ruta en su sesión gráfica de Webots, verificar carril derecho, cero
colisiones y ausencia de U-turn, y publicar el video. No se declara una URL de
YouTube hasta que exista.
