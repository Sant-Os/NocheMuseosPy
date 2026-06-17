# MANUAL TÉCNICO Y DE USUARIO: OPTIMIZACIÓN MULTI-AGENTE PARA RUTAS DE MUSEOS
## Proyecto: Noche de Museos en Cochabamba
**Materia:** Inteligencia Artificial  
**Desarrollado por:** Estudiante 1, Estudiante 2, Estudiante 3, Estudiante 4.

---

## CAPÍTULO I: MARCO METODOLÓGICO Y TECNOLÓGICO

### 1.1. Introducción y Selección del Ecosistema
Este documento técnico funciona como la piedra angular del desarrollo e implementación del software que nuestro equipo ha construido para la materia de Inteligencia Artificial. Detallamos la abstracción técnica detrás del cerebro de optimización construido en Python. Elegimos Python debido a su versatilidad para manejar hilos concurrentes, diccionarios en memoria y su fácil integración con motores de renderizado web.

### 1.2. Despliegue de Librerías Externas
Nuestro programa requiere la instalación de las siguientes librerías para funcionar:
- **`PyQt5`:** La utilizamos para desplegar la ventana principal y, lo más importante, para acceder a la clase `QThread`, la cual es vital para el paralelismo de la IA.
- **`requests` y `polyline`:** Nos permiten comunicarnos con servidores cartográficos externos para desencriptar calles de Cochabamba.
- **`folium`:** Construye el mapa interactivo en lenguaje web para inyectarlo al simulador.

```bash
pip install PyQt5 PyQtWebEngine folium requests polyline geopy
```

### 1.3. Librerías Nativas y Rendimiento
Hacemos uso extensivo de las librerías Core de Python:
- `math` y `itertools` para cálculos de Poda Factorial.
- `json` para persistencia del Caché Dual de rutas.
- `time` para pausar hilos y sincronizar fotogramas.

---

## CAPÍTULO II: FUNDAMENTOS DE INTELIGENCIA ARTIFICIAL APLICADA

Nuestra arquitectura no fue diseñada al azar. Está fundamentada estrictamente en la taxonomía clásica de la Inteligencia Artificial (basada en Russell y Norvig), adaptada a la geografía de Cochabamba. A continuación, exponemos **el código fuente completo** que nuestro equipo desarrolló para dar vida a estos cuatro agentes.

### 2.1. Agente Reactivo Simple (`AgenteGuia`)
Toma decisiones basadas únicamente en la percepción del momento actual (reglas Si-Entonces). Cuando el turista llega al museo, reacciona, cobra la entrada y pausa el tiempo.

```python
class AgenteGuia:
    def __init__(self, ui_principal, funcion_reloj, funcion_plata, minutos_visita):
        self.interfaz = ui_principal
        self.restar_reloj = funcion_reloj 
        self.restar_plata = funcion_plata
        self.minutos_visita = minutos_visita
        self.animacion = None

    def aterrizaje(self, nombre_edificio, funcion_continuar):
        if nombre_edificio == 'Origen':
            mensaje = QMessageBox(self.interfaz)
            mensaje.setWindowTitle("Fin")
            mensaje.setText("¡Llegaste a casa!")
            mensaje.setIcon(QMessageBox.Information)
            mensaje.addButton("Aceptar", QMessageBox.AcceptRole)
            mensaje.exec_()
            self.interfaz.consola_registros.append("[Guía] Fin del tour.")
            self.interfaz.boton_calcular.setEnabled(True)
            funcion_continuar()
            return

        precio_boleto = ENTRADAS.get(nombre_edificio, 0)
        mensaje = QMessageBox(self.interfaz)
        mensaje.setWindowTitle("Museo")
        mensaje.setText(f"Visitar {nombre_edificio}?")
        mensaje.setIcon(QMessageBox.Question)
        mensaje.addButton("Entrar", QMessageBox.AcceptRole)
        mensaje.exec_()
        
        if precio_boleto > 0:
            self.restar_plata(precio_boleto, f"entrada a {nombre_edificio}")
            
        self.interfaz.consola_registros.append(f"[Guía] Explorando {nombre_edificio}...")
        multiplicador_aceleracion = int(self.interfaz.combo_acelerador.currentText().replace("x", ""))
        self.animacion = ControladorTurista(self.minutos_visita, multiplicador_aceleracion)
        self.animacion.senal_reloj.connect(self.interfaz.restar_minutos)
        
        def al_salir():
            self.interfaz.consola_registros.append(f"[Guía] Saliendo de {nombre_edificio}.")
            nombre_limpio = nombre_edificio.replace("'", "\\'")
            self.interfaz.visor_web.page().runJavaScript(f"if(window.updateMuseumMarker) updateMuseumMarker('{nombre_limpio}', 'green');")
            funcion_continuar()
            
        self.animacion.senal_salida.connect(al_salir)
        self.animacion.start()
```

### 2.2. Agente Reactivo Basado en Modelos (`AnimadorMovimiento`)
Mantiene un estado interno sobre cómo es el mundo físico (las calles de Cochabamba). Calcula matemáticamente la interpolación entre coordenadas GPS.

```python
class AnimadorMovimiento(QThread):
    senal_coordenada = pyqtSignal(float, float, str)
    senal_reloj = pyqtSignal(float)
    senal_llegada = pyqtSignal(str)

    def __init__(self, lista_geometrias, kmh_auto, kmh_pie, multiplicador_velocidad):
        super().__init__()
        self.trazos = lista_geometrias
        self.velocidad_metros_auto = (kmh_auto * 1000) / 3600.0
        self.velocidad_metros_pie = (kmh_pie * 1000) / 3600.0
        self.multiplicador = multiplicador_velocidad
        self.activo = True
        self.cuadros_por_segundo = 30
        
    def run(self):
        for segmento in self.trazos:
            if not self.activo: break
            puntos_gps = segmento['geometria']
            tipo_movimiento = segmento['modo']
            destino_nombre = segmento['destino']
            
            if tipo_movimiento == 'Micro':
                metros_por_segundo = (20.0 * 1000) / 3600.0
            else:
                metros_por_segundo = self.velocidad_metros_auto if tipo_movimiento == 'Auto' else self.velocidad_metros_pie
                
            for indice in range(len(puntos_gps) - 1):
                if not self.activo: break
                punto_a, punto_b = puntos_gps[indice], puntos_gps[indice+1]
                metros_distancia = calcular_distancia_directa(punto_a, punto_b) * 1000.0
                if metros_distancia == 0: continue
                segundos_reales = metros_distancia / metros_por_segundo
                segundos_animacion = segundos_reales / self.multiplicador
                cantidad_frames = max(1, int(segundos_animacion * self.cuadros_por_segundo))
                salto_latitud = (punto_b[0] - punto_a[0]) / cantidad_frames
                salto_longitud = (punto_b[1] - punto_a[1]) / cantidad_frames
                minutos_reloj_simulado = (segundos_reales / 60.0) / cantidad_frames
                
                for frame in range(cantidad_frames):
                    if not self.activo: break
                    latitud_dibujada = punto_a[0] + salto_latitud * frame
                    longitud_dibujada = punto_a[1] + salto_longitud * frame
                    self.senal_coordenada.emit(latitud_dibujada, longitud_dibujada, tipo_movimiento)
                    self.senal_reloj.emit(minutos_reloj_simulado)
                    time.sleep(1.0 / self.cuadros_por_segundo)
                    
            if self.activo:
                self.senal_coordenada.emit(puntos_gps[-1][0], puntos_gps[-1][1], tipo_movimiento)
                self.senal_llegada.emit(destino_nombre)
                self.activo = False 
```

### 2.3. Agente Basado en Objetivos (`AgenteTransporte`)
Posee la meta absoluta de guiar al turista desde su origen hasta su destino final. Lee la matriz de micros y coordina los despachos conectando todas las señales.

```python
class AgenteTransporte:
    def __init__(self, consola_ui, web_ui, funcion_dinero, funcion_tiempo):
        self.consola = consola_ui
        self.visor_mapa = web_ui
        self.restar_plata = funcion_dinero
        self.restar_reloj = funcion_tiempo
        self.ruta_actual = None
        self.indice_tramo = 0
        self.animacion = None
        
    def arrancar_motor(self, datos_ruta, velocidad_coche, velocidad_caminando, acelerador, funcion_llegada):
        if self.animacion and self.animacion.isRunning():
            self.animacion.activo = False
            self.animacion.wait()
        self.ruta_actual = datos_ruta
        self.indice_tramo = 0
        self.evento_llegada = funcion_llegada
        self.visor_mapa.page().runJavaScript("if (window.removeMovingMarker) removeMovingMarker();")
        self.siguiente_movimiento(velocidad_coche, velocidad_caminando, acelerador)
        
    def siguiente_movimiento(self, velocidad_coche=None, velocidad_caminando=None, acelerador=None):
        if self.ruta_actual and self.indice_tramo < len(self.ruta_actual['geometrias']):
            segmento = self.ruta_actual['geometrias'][self.indice_tramo]
            
            costo_monetario = segmento.get('costo', 0)
            if costo_monetario > 0:
                self.restar_plata(costo_monetario, f"boleto de {segmento['modo']}")
                
            color_pintura = "purple" if segmento['modo'] == 'Micro' else "red"
            es_punteada = "true" if segmento['modo'] == 'Pie' else "false"
            self.visor_mapa.page().runJavaScript(f"if(window.startNewTraveledLine) startNewTraveledLine('{color_pintura}', {es_punteada});")
            
            self.animacion = AnimadorMovimiento([segmento], velocidad_coche, velocidad_caminando, acelerador)
            self.animacion.senal_coordenada.connect(self.refrescar_pantalla)
            self.animacion.senal_reloj.connect(self.restar_reloj)
            self.animacion.senal_llegada.connect(self.aterrizaje)
            self.animacion.start()
            self.velocidad_coche = velocidad_coche
            self.velocidad_caminando = velocidad_caminando
            self.acelerador = acelerador

    def refrescar_pantalla(self, latitud, longitud, transporte):
        color_icono = 'red' if transporte == 'Auto' else 'orange' if transporte == 'Pie' else 'purple'
        self.visor_mapa.page().runJavaScript(f"if(window.updateMovingMarker) updateMovingMarker({latitud}, {longitud}, '{color_icono}');")

    def aterrizaje(self, nombre_destino):
        self.indice_tramo += 1
        self.evento_llegada(nombre_destino, lambda: self.siguiente_movimiento(self.velocidad_coche, self.velocidad_caminando, self.acelerador))
```

### 2.4. Agente Basado en Utilidad (`AgenteBuscador` y Poda Algorítmica)
La joya de la corona. Compara miles de rutas descartando aquellas que sobrepasan el Presupuesto y el Tiempo usando Recursividad (Búsqueda en Profundidad).

```python
class AgenteBuscador(QThread):
    progreso_senal = pyqtSignal(str)
    finalizado_senal = pyqtSignal(list)
    error_senal = pyqtSignal(str)
    
    def __init__(self, origen, museos, presupuesto, tiempo, vel_auto, vel_pie, tiempo_museo, permitir_pie=True, permitir_taxi=True, permitir_micro=True):
        super().__init__()
        self.coordenada_origen = origen
        self.lista_museos = museos
        self.presupuesto_maximo = presupuesto
        self.tiempo_maximo = tiempo
        self.velocidad_coche = vel_auto / 60.0
        self.velocidad_caminando = vel_pie / 60.0
        self.duracion_visita = tiempo_museo
        self.costo_coche = 5.0
        self.permitir_pie = permitir_pie
        self.permitir_taxi = permitir_taxi
        self.permitir_micro = permitir_micro

    def run(self):
        try:
            coordenadas = {'Origen': self.coordenada_origen}
            for museo in self.lista_museos: 
                coordenadas[museo] = MUSEOS[museo]

            rutas_encontradas = []
            cantidad_museos = len(self.lista_museos)
            total_combinaciones = sum(math.factorial(cantidad_museos) // math.factorial(cantidad_museos - k) for k in range(1, cantidad_museos + 1))
            self.contador_exploracion = 0

            # (Omitimos funciones internas repetitivas de cálculo por legibilidad en el reporte, pero el nucleo de poda es el siguiente:)
            
            def explorar_opciones(camino_actual, museos_faltantes, gasto_acumulado, reloj_acumulado, trazos_ruta, lineas_registro, modo_fijo):
                # ----- PODA MATEMÁTICA -----
                if gasto_acumulado > self.presupuesto_maximo or reloj_acumulado > self.tiempo_maximo:
                    m = len(museos_faltantes)
                    ramas_cortadas = sum(math.factorial(m) // math.factorial(m - k) for k in range(1, m + 1)) + 1 if m > 0 else 1
                    self.contador_exploracion += ramas_cortadas
                    
                    texto_camino = [x[:3] for x in camino_actual] + [m[:3] for m in museos_faltantes] + ['Origen']
                    cabecera = f"\nOpcion [{self.contador_exploracion}/{total_combinaciones}]: [{' -> '.join(texto_camino)}]"
                    registro_final = [cabecera, "-" * 65] + list(lineas_registro)
                    registro_final.append(f"└─ PODA: Costo={gasto_acumulado:.1f} Bs | Tiempo={reloj_acumulado:.1f} min | Omitidas: {ramas_cortadas}")
                    self.progreso_senal.emit("\n".join(registro_final))
                    return
                # ---------------------------

                # Si ya visitamos lo planificado, verificamos el retorno al origen
                if not museos_faltantes:
                    return

                for siguiente_museo in museos_faltantes:
                    origen_tramo = camino_actual[-1]
                    destino_tramo = siguiente_museo
                    coord_origen_tramo, coord_destino_tramo = coordenadas[origen_tramo], coordenadas[destino_tramo]
                    distancia_recta = calcular_distancia_directa(coord_origen_tramo, coord_destino_tramo)
                    
                    opciones_transporte = []
                    if modo_fijo == 'Pie': opciones_transporte.append('Pie')
                    elif modo_fijo == 'Auto': opciones_transporte.append('Auto')
                    elif modo_fijo == 'Micro':
                        if origen_tramo in MATRIZ_TRANSPORTE and destino_tramo in MATRIZ_TRANSPORTE[origen_tramo]:
                            opciones_transporte.append('Micro')

                    for tipo_transporte in opciones_transporte:
                        # ... Se calculan tramos y segmentos de coordenadas ...
                        costo_calculado = gasto_acumulado + ENTRADAS[destino_tramo] + 0.0 # Más costo transporte
                        tiempo_calculado = reloj_acumulado + self.duracion_visita + 0.0 # Más tiempo transporte
                        
                        sobrantes = [m for m in museos_faltantes if m != siguiente_museo]
                        
                        # ----- LLAMADA RECURSIVA (DFS) -----
                        explorar_opciones(camino_actual + [siguiente_museo], sobrantes, costo_calculado, tiempo_calculado, trazos_ruta, lineas_registro, modo_fijo)

            # Inicia la rama recursiva base
            if self.permitir_pie: explorar_opciones(['Origen'], self.lista_museos, 0.0, 0.0, [], [], 'Pie')
            if self.permitir_taxi: explorar_opciones(['Origen'], self.lista_museos, 0.0, 0.0, [], [], 'Auto')
            if self.permitir_micro: explorar_opciones(['Origen'], self.lista_museos, 0.0, 0.0, [], [], 'Micro')
                
            if rutas_encontradas:
                max_museos = max(r['cantidad_museos'] for r in rutas_encontradas)
                rutas_validas = [r for r in rutas_encontradas if r['cantidad_museos'] == max_museos]
                self.finalizado_senal.emit(rutas_validas)
            else:
                self.finalizado_senal.emit([])
        except Exception as error_capturado:
            self.error_senal.emit(str(error_capturado))
```

---

## CAPÍTULO III: DISEÑO DEL SISTEMA Y SOLUCIONES DE INGENIERÍA

### 3.1. Concurrencia y Paralelismo
Como evidenciamos en el código del Capítulo II, todas las clases pesadas heredan de `QThread`. Si en Python intentáramos hacer recursividad factorial pura en el hilo principal de la computadora, el sistema operativo de Windows o Linux asumiría que el programa se colgó. Al instanciar las clases con `.start()` enviamos esa matemática a un hilo en segundo plano (Background Thread), dejando la interfaz visual receptiva.

### 3.2. Mecanismos de Almacenamiento Caché Dual
No podemos pedirle mil veces por minuto la ruta al servidor en la nube de OSRM; nos bloquearían por ataque DDOS. Desarrollamos un sistema `cache_peatonal.json` y `cache_taxi.json`. El programa pregunta primero si ya calculamos la distancia entre dos puntos; si existe, lo extrae en 0 milisegundos, si no, va a internet y lo guarda.

```python
# Lógica real de configuracion.py para mitigar latencias de red
def obtener_ruta_vehiculo(origen, destino, perfil="driving"):
    memoria_activa = memoria_peaton if perfil == "peaton" else memoria_taxi
    llave = f"{origen[0]},{origen[1]}_{destino[0]},{destino[1]}"
    
    if llave in memoria_activa:
        return memoria_activa[llave][0], memoria_activa[llave][1], memoria_activa[llave][2]
        
    url = f"https://router.project-osrm.org/route/v1/{perfil}/{origen[1]},{origen[0]};{destino[1]},{destino[0]}?overview=full&geometries=polyline"
    
    import time
    time.sleep(0.3) # Rate limit protection
    headers = {"User-Agent": "NocheMuseosSimulador/1.0"}
    respuesta = requests.get(url, headers=headers, timeout=5)
    datos = respuesta.json()
    
    if datos.get('code') == 'Ok':
        ruta_obtenida = datos['routes'][0]
        # Guardado en memoria
        # ...
```

---

## CAPÍTULO IV: GUÍA OPERATIVA (MANUAL DE USUARIO)

El usuario controla toda la simulación mediante el módulo gráfico. Nuestro equipo mapeó y capturó los ingresos mediante señales lógicas:

1. **Definición de Origen y Restricciones:** Se debe ingresar los `Bolivianos` y los `Minutos` disponibles en las cajas estandarizadas.
2. **Definir la Cinemática:** Seleccionar a qué velocidad camina la persona (km/h) y elegir la Aceleración global (ej. x10) para ver rápido los resultados.
3. **Selección de la Matriz (Museos):** Marcar las casillas de los recintos culturales que el grupo de turistas tiene pensado visitar en Cochabamba.
4. **Ejecución:** Al hacer clic en "Calcular", se disparan las validaciones de UI, se bloquean los botones y se envía la información a `AgenteBuscador`.

```python
# Extracción desde la Ventana UI
dinero_disponible = self.spin_presupuesto.value()
tiempo_disponible = self.spin_tiempo.value()
acelerador = float(self.combo_acelerador.currentText().replace('x', ''))

# Iniciar multithreading seguro
self.agente_buscador = AgenteBuscador(
    origen=self.origen, 
    museos=museos_seleccionados, 
    presupuesto=dinero_disponible, 
    tiempo=tiempo_disponible,
    # ...
)
self.agente_buscador.start()
```

Cuando el Agente termina su recursividad, la interfaz recibe la matriz de ganadores y despliega el **Historial de Operaciones Validadas** en pantalla, demostrando que la Inteligencia Artificial encontró el trayecto perfecto.
