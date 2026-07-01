# Validación técnica en Webots R2025a

Fecha de ejecución: 27 de junio de 2026. Revalidación de videos: 29 de junio
de 2026. Entorno: Webots R2025a, SUMO 1.27.1, macOS.

## Evidencia obtenida

| Ruta | Comando | Evidencia | Resultado |
|---|---:|---|---|
| Recto | 0 | Autobús reconocido a 23.74 m; 16.62 m de holgura LiDAR al iniciar; corredor de evasión limitado a `y>=232.60` | Sin contacto ni cruce de la doble línea; mínimo observado `y=232.77`, retorno y permanencia en `y=236.40`, llegada `GPS=(-188.06,236.40)` |
| Derecha | 2 | Peatón confirmado por Recognition + LiDAR; alto completo antes de la intersección hasta la fase verde | `FRENO_PEATON`, `ALTO_SEMAFORO`, liberación en verde a `t=51.84 s`, cruce despejado y llegada `GPS=(28.95,-67.48)` |
| Izquierda | 1 | Inicio de giro retrasado hasta el interior del cruce y asistencia lateral de salida | Giro contenido y permanencia en el carril derecho este `y=39.60`; llegada `GPS=(35.00,39.60)` |

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

| Ruta | Archivo de entrega | Duración | Evidencia del recorrido |
|---|---|---:|---|
| Recta | `Equipo19_Ruta_Recta.mp4` | 53.267 s | Evasión contenida en el sentido legal, separación visible del autobús, retorno al centro `y=236.40` y permanencia en el carril hasta la llegada |
| Derecha | `Equipo19_Ruta_Derecha.mp4` | 63.967 s | Freno ante peatón, espera fuera del cruce hasta verde, giro derecho y llegada |
| Izquierda | `Equipo19_Ruta_Izquierda.mp4` | 33.167 s | Giro izquierdo profundo, salida al carril derecho este y llegada |

Los tres MP4 usan H.264, resolución nativa de 1920 x 1080 px y 30 fps.
Una cámara de evidencia independiente sigue la posición del vehículo en ejes
globales, sin rotar con las correcciones de dirección. El encuadre se validó
mediante hojas de contacto de cada recorrido: el vehículo permanece visible y
se conserva contexto de carriles, peatones y tráfico. `ffmpeg` decodificó cada
archivo completo sin errores. No se observan colisiones, salida del recorrido
ni U-turn. La duración acumulada es 2:30.401, por debajo del máximo de seis
minutos para la posterior edición del video final.

SHA-256 de las copias de entrega:

- Recta: `c6f30632562925249aa47291baa69beb6cf7ecfafe21b701c9d03c54a07a9439`.
- Derecha: `06492c33d9112b1175c47ad13fd7bcc3d91d86ecc1f1271fe79e16eec3fec5a0`.
- Izquierda: `2b66e47fd5b65e4db57c44c85920d139e53246eb17a6cf8ab56c76541fd325b5`.

## Alcance de esta validación

Las ejecuciones finales terminaron con `RUTA COMPLETA`, por carril derecho, sin
colisión ni U-turn. La revalidación aumentó la anticipación y redujo la velocidad
ante el autobús. La evasión recta ahora usa una referencia lateral `y=233.20`,
un límite de seguridad `y=232.60`, adquisición confirmada de la pared derecha y
reincorporación amortiguada; la corrida final mantuvo el centro en `y>=232.77`
sin tocar la doble línea. Después de reincorporarse, un control lateral continuo
mantiene el vehículo en el centro original `y=236.40` hasta el destino. También
incorporó retorno lateral tras la evasión, añadió un alto
fuera de la intersección hasta la fase verde antes del giro derecho y corrigió el arco izquierdo para salir
en `y=39.60`. También conserva la corrección que distingue `BusSimple` del
mobiliario `bus stop`. Las diecisiete pruebas automatizadas volvieron a pasar y los tres mundos conservan
`maxVehicles 30`, Camera Recognition, LiDAR, radar, giroscopio y los tres
sensores laterales.

Video final publicado en YouTube: https://youtu.be/YObQTAm8_VM
