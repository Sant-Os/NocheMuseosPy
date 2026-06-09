import time
import math
import itertools
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QMessageBox
from configuracion import calcular_distancia_haversine, obtener_ruta_osrm, ENTRADAS, MUSEOS

class AgenteBuscadorInterno(QThread):
    progress = pyqtSignal(str)
    finished = pyqtSignal(list)
    error = pyqtSignal(str)
    def __init__(self, coords_origen, museos_seleccionados, presupuesto_max, tiempo_maximo, velocidad_auto, velocidad_pie, tiempo_por_museo):
        super().__init__()
        self.coords_origen = coords_origen
        self.museos_seleccionados = museos_seleccionados
        self.presupuesto_max = presupuesto_max
        self.tiempo_maximo = tiempo_maximo
        self.velocidad_auto = velocidad_auto / 60.0
        self.velocidad_pie = velocidad_pie / 60.0
        self.tiempo_por_museo = tiempo_por_museo
        self.costo_por_km_auto = 2.0       
        self.costo_por_km_pie = 0.0

    def run(self):
        try:
            coords = {'Origen': self.coords_origen}
            for m in self.museos_seleccionados: coords[m] = MUSEOS[m]

            def short(name):
                return name[:3] if name.startswith('[') else name

            rutas_validas = []
            n_museos = len(self.museos_seleccionados)
            total_perms = sum(math.factorial(n_museos) // math.factorial(n_museos - k) for k in range(1, n_museos + 1))
            self.count = 0
            def explorar_rama(ruta_actual, museos_pendientes, costo_acumulado, tiempo_acumulado, detalles_ruta, log_lines):
                if costo_acumulado > self.presupuesto_max or tiempo_acumulado > self.tiempo_maximo:
                    m = len(museos_pendientes)
                    podadas = sum(math.factorial(m) // math.factorial(m - k) for k in range(1, m + 1)) + 1 if m > 0 else 1
                    self.count += podadas
                    ruta_display = [short(x) for x in ruta_actual] + [short(m) for m in museos_pendientes] + ['Origen']
                    encabezado = f"\nPermutación [{self.count}/{total_perms}]: [{' -> '.join(ruta_display)}]"
                    log_f = [encabezado, "-" * 65] + list(log_lines)
                    log_f.append(f"└─ PODA: Costo={costo_acumulado:.1f} Bs | Tiempo={tiempo_acumulado:.1f} min | Descartadas: {podadas} permutación(es)")
                    self.progress.emit("\n".join(log_f))
                    return

                if len(ruta_actual) > 1:
                    self.count += 1
                    n1 = ruta_actual[-1]
                    n2 = 'Origen'
                    c1 = coords[n1]
                    c2 = coords[n2]
                    d = calcular_distancia_haversine(c1, c2)
                    modo = 'Pie' if d < 0.5 else 'Auto'
                    modo_str = 'driving' if modo == 'Auto' else 'foot'
                    distancia_km, t_min, geom = obtener_ruta_osrm(c1, c2, modo_str)
                    if distancia_km is None:
                        distancia_km = d * 1.3
                        geom = [c1, c2]
                    t_min_custom = distancia_km / self.velocidad_pie if modo == 'Pie' else distancia_km / self.velocidad_auto
                    costo_final = costo_acumulado + (distancia_km * self.costo_por_km_auto if modo == 'Auto' else 0)
                    tiempo_final = tiempo_acumulado + t_min_custom
                    ruta_display = [short(x) for x in ruta_actual] + ['Origen']
                    encabezado = f"\nPermutación [{self.count}/{total_perms}]: [{' -> '.join(ruta_display)}]"
                    log_f = [encabezado, "-" * 65] + list(log_lines)
                    log_f.append(f"|  -> {short(n2):<15} | {distancia_km:>6.2f} km | {t_min_custom:>5.1f} min | {modo}")
                    if costo_final <= self.presupuesto_max and tiempo_final <= self.tiempo_maximo:
                        estado = "✔ Válida"
                        log_f.append(f"└─ Costo: {costo_final:.1f} Bs | Tiempo: {tiempo_final:.1f} min | {estado}")
                        self.progress.emit("\n".join(log_f))
                        ruta_completa = ruta_actual + ['Origen']
                        detalles_completos = detalles_ruta + [{
                            'origen': n1, 'destino': n2, 'modo': modo,
                            'distancia': distancia_km, 'tiempo': t_min_custom, 'geometria': geom
                        }]
                        modos_completos = [d['modo'] for d in detalles_completos]
                        rutas_validas.append({
                            'nombre': " -> ".join([short(x) for x in ruta_actual[1:]]),
                            'num_museos': len(ruta_actual) - 1,
                            'ruta': ruta_completa, 'modos': modos_completos, 'costo': costo_final,
                            'tiempo': tiempo_final, 'detalles_ruta': detalles_completos, 'museos': self.museos_seleccionados
                        })
                    else:
                        estado = "✘ Descartada (Retorno excede límite)"
                        log_f.append(f"└─ Costo: {costo_final:.1f} Bs | Tiempo: {tiempo_final:.1f} min | {estado}")
                        self.progress.emit("\n".join(log_f))
                if not museos_pendientes:
                    return

                for siguiente in museos_pendientes:
                    n1 = ruta_actual[-1]
                    n2 = siguiente
                    c1 = coords[n1]
                    c2 = coords[n2]
                    d = calcular_distancia_haversine(c1, c2)
                    modo = 'Pie' if d < 0.5 else 'Auto'
                    modo_str = 'driving' if modo == 'Auto' else 'foot'
                    distancia_km, t_min, geom = obtener_ruta_osrm(c1, c2, modo_str)
                    if distancia_km is None:
                        distancia_km = d * 1.3
                        geom = [c1, c2]
                    t_min_custom = distancia_km / self.velocidad_pie if modo == 'Pie' else distancia_km / self.velocidad_auto
                    nuevo_costo = costo_acumulado + ENTRADAS[n2] + (distancia_km * self.costo_por_km_auto if modo == 'Auto' else 0)
                    nuevo_tiempo = tiempo_acumulado + self.tiempo_por_museo + t_min_custom
                    nueva_linea = f"|  -> {short(n2):<15} | {distancia_km:>6.2f} km | {t_min_custom:>5.1f} min | {modo}"
                    nuevo_detalles = detalles_ruta + [{
                        'origen': n1, 'destino': n2, 'modo': modo,
                        'distancia': distancia_km, 'tiempo': t_min_custom, 'geometria': geom
                    }]
                    nuevos_pendientes = [m for m in museos_pendientes if m != siguiente]
                    explorar_rama(ruta_actual + [siguiente], nuevos_pendientes, nuevo_costo, nuevo_tiempo, nuevo_detalles, log_lines + [nueva_linea])

            explorar_rama(['Origen'], self.museos_seleccionados, 0.0, 0.0, [], [])
            rutas_validas.sort(key=lambda x: (x['costo'], x['tiempo']))
            self.finished.emit(rutas_validas)
        except Exception as e:
            self.error.emit(str(e))

class HiloAnimacion(QThread):
    actualizar_posicion = pyqtSignal(float, float, str)
    tick_tiempo = pyqtSignal(float)
    tramo_terminado = pyqtSignal(str)

    def __init__(self, ruta_detalles, vel_auto_kmh, vel_pie_kmh, multiplicador):
        super().__init__()
        self.detalles_ruta = ruta_detalles
        self.vel_auto_ms = (vel_auto_kmh * 1000) / 3600.0
        self.vel_pie_ms = (vel_pie_kmh * 1000) / 3600.0
        self.multiplicador = multiplicador
        self.esta_corriendo = True
        self.fps = 30
    def run(self):
        for tramo in self.detalles_ruta:
            if not self.esta_corriendo: break
            geom = tramo['geometria']
            modo = tramo['modo']
            destino = tramo['destino']
            speed_ms = self.vel_auto_ms if modo == 'Auto' else self.vel_pie_ms
            for i in range(len(geom) - 1):
                if not self.esta_corriendo: break
                p1, p2 = geom[i], geom[i+1]
                dist_meters = calcular_distancia_haversine(p1, p2) * 1000.0
                if dist_meters == 0: continue
                tiempo_real_seg = dist_meters / speed_ms
                simulated_time_sec = tiempo_real_seg / self.multiplicador
                cuadros = max(1, int(simulated_time_sec * self.fps))
                dlat = (p2[0] - p1[0]) / cuadros
                dlon = (p2[1] - p1[1]) / cuadros
                min_simulados_por_cuadro = (tiempo_real_seg / 60.0) / cuadros
                for f in range(cuadros):
                    if not self.esta_corriendo: break
                    lat_actual = p1[0] + dlat * f
                    lon_actual = p1[1] + dlon * f
                    self.actualizar_posicion.emit(lat_actual, lon_actual, modo)
                    self.tick_tiempo.emit(min_simulados_por_cuadro)
                    time.sleep(1.0 / self.fps)
            if self.esta_corriendo:
                self.actualizar_posicion.emit(geom[-1][0], geom[-1][1], modo)
                self.tramo_terminado.emit(destino)
                self.esta_corriendo = False 

class HiloVisita(QThread):
    tick_tiempo = pyqtSignal(float)
    visita_terminada = pyqtSignal()
    def __init__(self, t_museo_minutos, multiplicador):
        super().__init__()
        self.t_museo_minutos = t_museo_minutos
        self.multiplicador = multiplicador
        self.fps = 10
    def run(self):
        tiempo_real_seg = (self.t_museo_minutos * 60) / self.multiplicador
        cuadros = max(1, int(tiempo_real_seg * self.fps))
        min_simulados_por_cuadro = self.t_museo_minutos / cuadros
        for f in range(cuadros):
            self.tick_tiempo.emit(min_simulados_por_cuadro)
            time.sleep(1.0 / self.fps)
        self.visita_terminada.emit()

class AgenteTransporte:
    def __init__(self, log_widget, vista_web, restar_dinero_cb, tick_tiempo_cb):
        self.log_widget = log_widget
        self.vista_web = vista_web
        self.restar_dinero_cb = restar_dinero_cb
        self.tick_tiempo_cb = tick_tiempo_cb
        self.ruta_actual = None
        self.paso_actual = 0
        self.hilo_animacion = None
        self.costo_por_km_auto = 2.0
    def log(self, mensaje):
        self.log_widget.append(f"[Agente Transporte] {mensaje}")
    def iniciar_ruta(self, ruta_info, velocidad_auto, velocidad_pie, multiplicador, on_llegada):
        if self.hilo_animacion and self.hilo_animacion.isRunning():
            self.hilo_animacion.esta_corriendo = False
            self.hilo_animacion.wait()
        self.ruta_actual = ruta_info
        self.paso_actual = 0
        self.on_llegada_callback = on_llegada
        self.vista_web.page().runJavaScript("if (window.removeMovingMarker) removeMovingMarker();")
        self.log(f"¡Iniciando simulación! (Multiplicador x{multiplicador})")
        self.ejecutar_siguiente_paso(velocidad_auto, velocidad_pie, multiplicador)
    def ejecutar_siguiente_paso(self, velocidad_auto=None, velocidad_pie=None, multiplicador=None):
        if self.ruta_actual and self.paso_actual < len(self.ruta_actual['detalles_ruta']):
            tramo = self.ruta_actual['detalles_ruta'][self.paso_actual]
            self.log(f"Viajando hacia {tramo['destino']} en {tramo['modo']} ({tramo['distancia']:.2f} km)...")
            if tramo['modo'] == 'Auto':
                costo_viaje = tramo['distancia'] * self.costo_por_km_auto
                self.restar_dinero_cb(costo_viaje, f"Taxi a {tramo['destino']}")
            color_recorrido = "red"
            estilo_linea = "true" if tramo['modo'] == 'Pie' else "false"
            self.vista_web.page().runJavaScript(f"if(window.startNewTraveledLine) startNewTraveledLine('{color_recorrido}', {estilo_linea});")
            self.hilo_animacion = HiloAnimacion([tramo], velocidad_auto, velocidad_pie, multiplicador)
            self.hilo_animacion.actualizar_posicion.connect(self.actualizar_marcador)
            self.hilo_animacion.tick_tiempo.connect(self.tick_tiempo_cb)
            self.hilo_animacion.tramo_terminado.connect(self.procesar_llegada)
            self.hilo_animacion.start()
            self.velocidad_auto = velocidad_auto
            self.velocidad_pie = velocidad_pie
            self.multiplicador = multiplicador
        else:
            self.log("¡Ruta finalizada con éxito!")

    def actualizar_marcador(self, lat, lon, modo):
        color = 'red' if modo == 'Auto' else 'orange'
        self.vista_web.page().runJavaScript(f"if(window.updateMovingMarker) updateMovingMarker({lat}, {lon}, '{color}');")

    def procesar_llegada(self, destino):
        self.log(f"Llegada confirmada a {destino}.")
        self.paso_actual += 1
        self.on_llegada_callback(destino, lambda: self.ejecutar_siguiente_paso(self.velocidad_auto, self.velocidad_pie, self.multiplicador))

class AgenteGuiaLocal:
    def __init__(self, parent, reloj_cb, dinero_cb, t_museo):
        self.parent = parent
        self.reloj_cb = reloj_cb 
        self.dinero_cb = dinero_cb
        self.t_museo = t_museo
        self.hilo_visita = None

    def procesar_llegada(self, museo, callback_continuar):
        if museo == 'Origen':
            msg = QMessageBox(self.parent)
            msg.setWindowTitle("Fin del Recorrido")
            msg.setText("¡Has llegado de vuelta a casa!\nEl recorrido ha finalizado con éxito.")
            msg.setIcon(QMessageBox.Information)
            msg.addButton("Finalizar", QMessageBox.AcceptRole)
            msg.exec_()
            self.parent.consola_registros.append("[Sistema] Recorrido completado exitosamente.")
            self.parent.btn_calcular.setEnabled(True)
            callback_continuar()
            return

        costo_entrada = ENTRADAS.get(museo, 0)
        msg = QMessageBox(self.parent)
        msg.setWindowTitle("Agente Guía")
        msg.setText(f"¡Llegaste al {museo}!\n¿Confirmas la visita de {self.t_museo} min?")
        msg.setIcon(QMessageBox.Question)
        msg.addButton("Ingresar", QMessageBox.AcceptRole)
        msg.exec_()
        self.dinero_cb(costo_entrada, f"Entrada a {museo}")
        self.parent.consola_registros.append(f"[Agente Guía] Iniciando recorrido dentro de {museo}...")
        multi = int(self.parent.combo_multi.currentText().replace("x", ""))
        self.hilo_visita = HiloVisita(self.t_museo, multi)
        self.hilo_visita.tick_tiempo.connect(self.parent.descontar_tiempo_tick)
        def on_visit_done():
            self.parent.consola_registros.append(f"[Agente Guía] Visita concluida en {museo}.")
            nombre_js = museo.replace("'", "\\'")
            self.parent.vista_web.page().runJavaScript(f"if(window.updateMuseumMarker) updateMuseumMarker('{nombre_js}', 'green');")
            callback_continuar()
        self.hilo_visita.visita_terminada.connect(on_visit_done)
        self.hilo_visita.start()
