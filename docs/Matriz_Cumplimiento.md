# Matriz de cumplimiento - Proyecto Final

| Requisito | Evidencia prevista | Estado |
|---|---|---|
| Dataset automatico con imagen, angulo y comando | `cil_dataset_recorder.py` y CSV con encabezado | Completo |
| Velocidad de captura <=30 km/h | Constante `CRUISING_SPEED_KMH = 30.0` | Completo |
| Dataset final >10,000 | 12,956 muestras fisicas despues de aumento | Completo |
| Tres comandos | STRAIGHT, LEFT y RIGHT | Completo |
| Notebook inicia con clone de GitHub | Primera celda de codigo | Completo |
| Division sin fuga | `source_id` disjunto antes de aumento | Completo |
| Modelo exportado y usado en World 2 | `cil_model.h5` y metadatos | En validacion |
| Tres rutas con origen/destino | Tres presets World 2 | En validacion |
| Evasion de obstaculo | Recognition + LiDAR + pared derecha | En validacion |
| Peaton y freno de emergencia | Recognition + LiDAR, umbral 15 m | En validacion |
| Distancia a vehiculo | Radar, parada 12 m, reanudacion 15 m | En validacion |
| SUMO >=30 vehiculos | `maxVehicles 30` | Completo |
| Video <6 min y participa todo el equipo | Guion 5:35 y clips tecnicos | Pendiente de grabacion del equipo |
| Enlace de YouTube en reporte | Se inserta despues de publicar | Pendiente del equipo |
| Declaracion de IA | Seccion explicita en reporte | Completo |
