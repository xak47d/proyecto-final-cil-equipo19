# Matriz de cumplimiento - Proyecto Final

| Requisito | Evidencia |
|---|---|
| Dataset automatico con imagen, angulo y comando | `cil_dataset_recorder.py` y CSV con encabezado |
| Velocidad de captura <=30 km/h | Constante `CRUISING_SPEED_KMH = 30.0` |
| Dataset final >10,000 | 12,956 muestras fisicas despues de aumento |
| Tres comandos | STRAIGHT, LEFT y RIGHT |
| Notebook inicia con clone de GitHub | Primera celda de codigo |
| Division sin fuga | `source_id` disjunto antes de aumento |
| Modelo exportado y usado en World 2 | `cil_model.h5` y metadatos |
| Tres rutas con origen/destino | Tres presets y dos recorridos limpios por ruta |
| Evasion de obstaculo | Recognition + LiDAR + pared derecha; `y>=232.77` sin cruzar doble linea |
| Permanencia en carril tras evasion | Retorno y control lateral continuo en `y=236.40` |
| Peaton y freno de emergencia | Recognition + LiDAR, umbral 15 m |
| Distancia a vehiculo | Radar, parada 12 m, reanudacion 15 m |
| SUMO >=30 vehiculos | `maxVehicles 30` |
| Video final | Participacion del equipo y demostracion de las tres rutas |
| Enlace de YouTube | https://youtu.be/YObQTAm8_VM |
| Declaracion de IA | Seccion explicita en reporte |
