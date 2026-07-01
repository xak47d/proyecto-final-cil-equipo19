# Guion del video demostrativo - Equipo 19

Video final publicado: https://youtu.be/YObQTAm8_VM

Duracion objetivo: **5:35**. El video final debe conservar la participacion
visible o audible de los tres integrantes y mostrar Optional Rendering para
camara, LiDAR, radar y sensores de distancia.

Integrantes y reparto:
- **Jose Antonio Fernandez Perez** - Apertura (0:00) y Ruta izquierda (3:40).
- **Demenard Gardy Armand** - Dataset y red (0:35) e Integracion (4:35).
- **Raul Adrian Delgado Rodriguez** - Ruta recta (1:35) y Ruta derecha (2:40).

Cada bloque incluye las senales visuales (**En pantalla**) y el texto a decir
(**Locucion**). El texto esta pensado para leerse a ritmo natural dentro del
tiempo indicado.

---

## 0:00-0:35 - Apertura - Jose Antonio Fernandez Perez

**En pantalla:** titulo del proyecto y nombres del equipo; corte rapido a World 1
y World 2 con el vehiculo en marcha.

**Locucion:**
> Hola, somos el Equipo 19. En este video mostramos un sistema de conduccion
> autonoma basado en aprendizaje por imitacion, o CIL, que responde a tres
> comandos de navegacion: seguir recto, girar a la izquierda y girar a la
> derecha. Trabajamos sobre dos escenarios de Webots: World 1, donde capturamos
> los datos, y World 2, donde validamos el modelo. La velocidad de captura fue de
> 30 kilometros por hora, y en World 2 evaluamos a 22 kilometros por hora para
> dar margen a los mecanismos de seguridad. A continuacion les mostramos como se
> construyo el conjunto de datos y la red.

---

## 0:35-1:35 - Dataset y red - Demenard Gardy Armand

**En pantalla:** mosaico de imagenes del dataset; diagrama de la CNN; curvas de
MSE y MAE de entrenamiento y validacion.

**Locucion:**
> Partimos de 6,129 imagenes originales y, tras el aumento de datos, llegamos a
> 12,956 muestras finales. El aumento consiste en un reflejo horizontal de la
> imagen: invertimos el signo del angulo de direccion e intercambiamos el comando
> izquierda por derecha. Es importante senalar que la division por identificador
> de origen se hace antes de aumentar, asi que no hay fuga de informacion entre
> entrenamiento y validacion. La red es una CNN con cinco capas convolucionales;
> el comando se inyecta como vector one-hot y se combina con capas densas que
> producen el angulo de direccion. El entrenamiento usa el optimizador Adam con
> tasa de aprendizaje de 1 por 10 a la menos 4, perdida MSE y metrica MAE, 12
> epocas, lotes de 32, y los callbacks EarlyStopping y ReduceLROnPlateau con
> factor 0.5 y paciencia 2. Fijamos la semilla en 19 y la entrada es de 160 por
> 80 por 3, con un recorte del 25 por ciento superior. El resultado: un MAE de
> validacion global de 0.022 radianes; por comando, 0.015 en recto, 0.024 en
> izquierda y 0.023 en derecha, todos por debajo del objetivo de 0.05 radianes.

---

## 1:35-2:40 - Ruta recta - Raul Adrian Delgado Rodriguez

**En pantalla:** consola con `Cmd=STRAIGHT`; vista de radar y LiDAR; overlay del
GPS y del limite `y=232.60`.

**Locucion:**
> Esta es la ruta recta. Salimos de las torres residenciales del noreste con
> destino a los silos, y en consola se mantiene el comando STRAIGHT. La gestion
> de obstaculos frontales usa el radar con tres umbrales: empieza a regular la
> velocidad desde 25 metros, se detiene por completo a 12 metros y reanuda la
> marcha a 15 metros. Para evasion lateral el umbral esta configurado en 26
> metros; en esta corrida el autobus se reconocio a 23.74 metros y la maniobra
> inicio con 16.62 metros medidos por LiDAR. Observen el seguimiento de la pared
> derecha: esta contenido por el limite y igual a 232.60, y el minimo que
> registramos fue 232.77, sin tocar ni cruzar la doble linea. Despues de
> rebasar, el vehiculo se reincorpora y permanece en el centro del carril
> original, en y igual a 236.40, hasta llegar al destino con GPS en menos 188.06,
> 236.40.

---

## 2:40-3:40 - Ruta derecha y peaton - Raul Adrian Delgado Rodriguez

**En pantalla:** consola con `Cmd=RIGHT`; giro a la derecha; camara detectando al
peaton; distancia frontal del LiDAR y velocidad.

**Locucion:**
> Seguimos con la ruta a la derecha. Salimos del Subway norte hacia la iglesia, y
> el comando RIGHT genera un giro limpio a la derecha, sin vuelta en U. En esta
> ruta aparece un peaton: la camara lo reconoce y el LiDAR mide la distancia
> frontal. Con el umbral de 15 metros, el vehiculo baja a 0 kilometros por hora
> antes del cruce. Hace el alto antes de la interseccion y espera la fase verde
> del semaforo. Solo continua cuando el peaton deja la trayectoria y el semaforo
> habilita el cruce; en ese momento la navegacion retoma el control.

---

## 3:40-4:35 - Ruta izquierda - Jose Antonio Fernandez Perez

**En pantalla:** consola con `Cmd=LEFT`; giro a la izquierda; permanencia en el
carril derecho con el volante controlado por la CNN.

**Locucion:**
> Esta es la ruta a la izquierda. Salimos del parque infantil hacia el Subway
> norte; el comando LEFT ejecuta el giro y el vehiculo se mantiene en el carril
> derecho. Quiero destacar un punto de diseno: el volante lo sigue controlando la
> CNN en todo momento, salvo cuando el arbitro de seguridad necesita una anulacion
> temporal. Es decir, el modelo aprendido conduce, y la seguridad solo interviene
> cuando hace falta.

---

## 4:35-5:15 - Integracion y prioridades - Demenard Gardy Armand

**En pantalla:** diagrama del arbitro de seguridad con sus entradas (peaton,
autobus, radar, CIL); panel de SUMO con el trafico.

**Locucion:**
> Veamos como se integra todo. Este es el arbitro de seguridad, que prioriza
> cuatro entradas: peaton, autobus, radar y el comando CIL. La idea central es
> que la seguridad solo sustituye temporalmente la velocidad o la direccion; el
> comando de navegacion nunca se pierde, siempre se conserva. Asi combinamos un
> control aprendido con reglas de seguridad explicitas. Ademas, el trafico de
> SUMO esta configurado con 30 vehiculos, que no es menos de lo solicitado para
> la evaluacion.

---

## 5:15-5:35 - Cierre - Jose Antonio Fernandez Perez

**En pantalla:** los tres integrantes en pantalla o en cuadro; enlace del
repositorio y conclusiones.

**Locucion:**
> En resumen, logramos una conduccion autonoma por imitacion que responde a tres
> comandos y respeta los limites del carril, con un MAE de validacion de 0.022
> radianes y un arbitro de seguridad que protege sin perder la navegacion.
> Gracias por su atencion; el codigo esta disponible en el repositorio que
> aparece en pantalla.

Cerrar antes de 6:00.
