# Guion del video demostrativo - Equipo 19

Duracion objetivo: **5:35**. El video final debe conservar la participacion
visible o audible de los cuatro integrantes y mostrar Optional Rendering para
camara, LiDAR, radar y sensores de distancia.

## 0:00-0:35 - Apertura - Jose Antonio Fernandez Perez

- Presentar objetivo: conduccion CIL con comandos recto, izquierda y derecha.
- Mostrar brevemente World 1 y World 2.
- Indicar que la velocidad de captura fue 30 km/h y que World 2 se evalua a
  22 km/h para dar margen a los mecanismos de seguridad.

## 0:35-1:35 - Dataset y red - Demenard Gardy Armand

- Mostrar 6,129 imagenes originales y 12,956 muestras finales aumentadas.
- Explicar el aumento: reflejo horizontal con inversion del signo del angulo e
  intercambio de comando IZQUIERDA<->DERECHA. La division por `source_id` ocurre
  antes de aumentar, por lo que no hay fuga entre entrenamiento y validacion.
- Mostrar la CNN: cinco convoluciones, comando one-hot, capas densas y salida
  del angulo de direccion.
- Indicar los parametros de entrenamiento: optimizador Adam (lr 1e-4), perdida
  MSE y metrica MAE, 12 epocas, batch 32, callbacks EarlyStopping y
  ReduceLROnPlateau (factor 0.5, paciencia 2), semilla 19 y entrada 160x80x3 con
  recorte superior del 25 %.
- Mostrar curvas de MSE/MAE y leer el MAE de validacion: global 0.022 rad
  (STRAIGHT 0.015, LEFT 0.024, RIGHT 0.023; objetivo <= 0.05 rad).

## 1:35-2:40 - Ruta recta - Luis Daniel Castillo Alegria

- Origen: torres residenciales del noreste. Destino: silos.
- Mostrar `Cmd=STRAIGHT` en consola.
- Indicar los umbrales de radar: regulacion desde 25 m, parada a 12 m y
  reanudacion a 15 m.
- Indicar que el umbral de evasion esta configurado a 18 m; en la corrida el
  autobus se reconocio a ~11.7 m y se disparo el cambio de estado de evasion.
- Mostrar el seguimiento de pared derecha y la reincorporacion al carril derecho.

## 2:40-3:40 - Ruta derecha y peaton - Raul Adrian Delgado Rodriguez

- Origen: Subway norte. Destino: iglesia.
- Mostrar `Cmd=RIGHT` y el giro a la derecha sin U-turn.
- Mostrar el peaton reconocido por la camara y la distancia frontal del LiDAR.
- Indicar el umbral de 15 m y mostrar velocidad 0 km/h antes del cruce.
- Continuar cuando el peaton deje la trayectoria.

## 3:40-4:35 - Ruta izquierda - Jose Antonio Fernandez Perez

- Origen: parque infantil. Destino: Subway norte.
- Mostrar `Cmd=LEFT`, el giro y la permanencia en el carril derecho.
- Señalar que la CNN sigue controlando el volante cuando no hay una anulacion
  temporal del arbitro de seguridad.

## 4:35-5:15 - Integracion y prioridades - Demenard Gardy Armand

- Mostrar el diagrama del arbitro: peaton, autobus, radar y CIL.
- Explicar que la seguridad solo sustituye temporalmente velocidad/direccion;
  el comando de navegacion se conserva.
- Mostrar que SUMO esta limitado a 30 vehiculos, no menos de lo solicitado.

## 5:15-5:35 - Cierre - todos

- Cada integrante aparece en pantalla o confirma su participacion.
- Mostrar enlace del repositorio y conclusiones.
- Cerrar antes de 6:00.
