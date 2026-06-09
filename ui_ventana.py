import os
import json
import folium
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QSpinBox, QPushButton, 
                             QListWidget, QTextEdit, QMessageBox, QGroupBox, 
                             QLineEdit, QListWidgetItem, QComboBox)
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage
from PyQt5.QtCore import QUrl, pyqtSignal, Qt, QUrlQuery
from geopy.geocoders import Nominatim
from configuracion import MUSEOS
from agentes_ia import AgenteTransporte, AgenteGuiaLocal, AgenteBuscadorInterno

class PaginaMapaWeb(QWebEnginePage):
    map_clicked = pyqtSignal(float, float)
    def acceptNavigationRequest(self, url, _type, isMainFrame):
        if url.scheme() == "pyqt" and url.host() == "mapclick":
            query = QUrlQuery(url)
            lat = float(query.queryItemValue("lat"))
            lon = float(query.queryItemValue("lon"))
            self.map_clicked.emit(lat, lon)
            return False
        return super().acceptNavigationRequest(url, _type, isMainFrame)



class VentanaPrincipal(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Simulador de IA Avanzado: Noche de Museos")
        self.resize(1300, 850)
        self.tiempo_disponible = 0
        self.presupuesto_disponible = 0
        self.coords_origen = None
        self.geolocator = Nominatim(user_agent="noche_museos_sim")
        self.init_ui()
        self.actualizar_mapa()
        self.transporte = AgenteTransporte(self.consola_registros, self.vista_web, self.descontar_dinero, self.descontar_tiempo_tick)
        self.guia = None 

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        diseno_principal = QHBoxLayout(central_widget)
        diseno_izquierdo = QVBoxLayout()
        diseno_izquierdo.setContentsMargins(10, 10, 10, 10)
        group_inputs = QGroupBox("1. Origen y Presupuesto")
        form_layout = QVBoxLayout()
        form_layout.addWidget(QLabel("Dirección Origen (o HAZ CLIC EN EL MAPA):"))
        h_origen = QHBoxLayout()
        self.txt_origen = QLineEdit()
        self.txt_origen.setPlaceholderText("Ej. Plaza Cala Cala")
        h_origen.addWidget(self.txt_origen)
        self.btn_geolocalizar = QPushButton("Origen")
        self.btn_geolocalizar.setStyleSheet("background-color: #607D8B; color: white; padding: 4px 15px; font-weight: bold;")
        self.btn_geolocalizar.clicked.connect(self.fijar_origen)
        h_origen.addWidget(self.btn_geolocalizar)
        form_layout.addLayout(h_origen)
        h_presupuesto = QHBoxLayout()
        h_presupuesto.addWidget(QLabel("Presupuesto (Bs):"))
        self.spin_presupuesto = QSpinBox()
        self.spin_presupuesto.setRange(0, 5000)
        self.spin_presupuesto.setValue(0)
        h_presupuesto.addWidget(self.spin_presupuesto)
        h_presupuesto.addWidget(QLabel("Tiempo Total (min):"))
        self.spin_tiempo = QSpinBox()
        self.spin_tiempo.setRange(0, 1440)
        self.spin_tiempo.setValue(0)
        h_presupuesto.addWidget(self.spin_tiempo)
        form_layout.addLayout(h_presupuesto)
        group_inputs.setLayout(form_layout)
        diseno_izquierdo.addWidget(group_inputs)
        group_fisica = QGroupBox("2. Física y Simulación")
        f_fisica = QVBoxLayout()
        h1 = QHBoxLayout()
        h1.addWidget(QLabel("Velocidad Auto (km/h):"))
        self.spin_vauto = QSpinBox()
        self.spin_vauto.setRange(10, 150)
        self.spin_vauto.setValue(40)
        h1.addWidget(self.spin_vauto)
        h1.addWidget(QLabel("Vel. a Pie (km/h):"))
        self.spin_vpie = QSpinBox()
        self.spin_vpie.setRange(1, 15)
        self.spin_vpie.setValue(5)
        h1.addWidget(self.spin_vpie)
        f_fisica.addLayout(h1)
        h2 = QHBoxLayout()
        h2.addWidget(QLabel("Visita a Museos (min):"))
        self.spin_vmuseo = QSpinBox()
        self.spin_vmuseo.setRange(0, 120)
        self.spin_vmuseo.setValue(0)
        h2.addWidget(self.spin_vmuseo)
        h2.addWidget(QLabel("Acelerar Simulación:"))
        self.combo_multi = QComboBox()
        self.combo_multi.addItems(["x1", "x2", "x5", "x10", "x15", "x20", "x25"])
        self.combo_multi.setCurrentIndex(0)
        h2.addWidget(self.combo_multi)
        f_fisica.addLayout(h2)
        group_fisica.setLayout(f_fisica)
        diseno_izquierdo.addWidget(group_fisica)
        diseno_izquierdo.addWidget(QLabel("3. Selecciona los museos (Recomendado máx 6):"))
        self.lista_museos = QListWidget()
        self.lista_museos.setMaximumHeight(200)
        item_peatonal = QListWidgetItem("--- RUTA PEATONAL ---")
        item_peatonal.setFlags(Qt.NoItemFlags)
        font = item_peatonal.font()
        font.setBold(True)
        item_peatonal.setFont(font)
        item_peatonal.setForeground(Qt.blue)
        self.lista_museos.addItem(item_peatonal)
        for m in list(MUSEOS.keys())[:10]:
            item = QListWidgetItem(m)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Unchecked)
            self.lista_museos.addItem(item)
        item_movil = QListWidgetItem("--- RUTA MÓVIL ---")
        item_movil.setFlags(Qt.NoItemFlags)
        item_movil.setFont(font)
        item_movil.setForeground(Qt.blue)
        self.lista_museos.addItem(item_movil)
        for m in list(MUSEOS.keys())[10:]:
            item = QListWidgetItem(m)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Unchecked)
            self.lista_museos.addItem(item)
        self.lista_museos.itemChanged.connect(self.al_seleccionar_museo)
        diseno_izquierdo.addWidget(self.lista_museos)
        h_botones = QHBoxLayout()
        self.btn_calcular = QPushButton("Calcular")
        self.btn_calcular.setStyleSheet("background-color: #2196F3; color: white; font-weight: bold; padding: 4px 15px; font-size: 13px;")
        self.btn_calcular.clicked.connect(self.calcular_rutas)
        h_botones.addWidget(self.btn_calcular)
        self.btn_detener = QPushButton("Reiniciar")
        self.btn_detener.setStyleSheet("background-color: #F44336; color: white; font-weight: bold; padding: 4px 15px; font-size: 13px;")
        self.btn_detener.clicked.connect(self.detener_y_limpiar)
        h_botones.addWidget(self.btn_detener)
        diseno_izquierdo.addLayout(h_botones)

        v_rutas = QVBoxLayout()
        self.combo_rutas = QListWidget()
        self.combo_rutas.setMaximumHeight(80)
        self.combo_rutas.setEnabled(False)
        self.combo_rutas.setStyleSheet("padding: 5px; font-size: 12px;")
        self.combo_rutas.itemSelectionChanged.connect(self.previsualizar_ruta)
        self.btn_iniciar = QPushButton("Iniciar")
        self.btn_iniciar.setEnabled(False)
        self.btn_iniciar.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold; padding: 4px 15px; font-size: 13px;")
        self.btn_iniciar.clicked.connect(self.iniciar_recorrido_seleccionado)
        v_rutas.addWidget(self.combo_rutas)
        v_rutas.addWidget(self.btn_iniciar)
        diseno_izquierdo.addLayout(v_rutas)
        h_restantes = QHBoxLayout()
        self.lbl_tiempo_restante = QLabel("Tiempo: -")
        self.lbl_tiempo_restante.setStyleSheet("font-size: 14px; font-weight: bold; color: #E91E63; margin-top: 5px;")
        h_restantes.addWidget(self.lbl_tiempo_restante)
        self.lbl_dinero_restante = QLabel("Presupuesto: - Bs")
        self.lbl_dinero_restante.setStyleSheet("font-size: 14px; font-weight: bold; color: #2196F3; margin-top: 5px;")
        h_restantes.addWidget(self.lbl_dinero_restante)
        diseno_izquierdo.addLayout(h_restantes)
        self.consola_registros = QTextEdit()
        self.consola_registros.setReadOnly(True)
        self.consola_registros.setStyleSheet("background-color: #1E1E1E; color: #4CAF50; font-family: Consolas, monospace; font-size: 11px;")
        diseno_izquierdo.addWidget(self.consola_registros)
        diseno_principal.addLayout(diseno_izquierdo, stretch=1)
        diseno_derecho = QVBoxLayout()
        self.vista_web = QWebEngineView()
        self.pagina_mapa = PaginaMapaWeb(self.vista_web)
        self.pagina_mapa.map_clicked.connect(self.on_map_clicked)
        self.vista_web.setPage(self.pagina_mapa)
        diseno_derecho.addWidget(self.vista_web)
        diseno_principal.addLayout(diseno_derecho, stretch=3)

    def al_seleccionar_museo(self, item):
        if not (item.flags() & Qt.ItemIsUserCheckable): return
        color = "yellow" if item.checkState() == Qt.Checked else "red"
        nombre_js = item.text().replace("'", "\\'")
        self.vista_web.page().runJavaScript(f"if(window.updateMuseumMarker) updateMuseumMarker('{nombre_js}', '{color}');")

    def detener_y_limpiar(self):
        if self.transporte.hilo_animacion and self.transporte.hilo_animacion.isRunning():
            self.transporte.hilo_animacion.esta_corriendo = False
            self.transporte.hilo_animacion.wait()
        if hasattr(self, 'guia') and self.guia and hasattr(self.guia, 'hilo_visita'):
            try:
                self.guia.hilo_visita.terminate()
                self.guia.hilo_visita.wait()
            except: pass
        if hasattr(self, 'hilo_buscador') and self.hilo_buscador and self.hilo_buscador.isRunning():
            try:
                self.hilo_buscador.terminate()
                self.hilo_buscador.wait()
            except: pass
        self.btn_calcular.setEnabled(True)
        if hasattr(self, 'btn_iniciar'):
            self.btn_iniciar.setEnabled(False)
        if hasattr(self, 'combo_rutas'):
            self.combo_rutas.clear()
            self.combo_rutas.setEnabled(False)
        for i in range(self.lista_museos.count()):
            item = self.lista_museos.item(i)
            if item.flags() & Qt.ItemIsUserCheckable:
                item.setCheckState(Qt.Unchecked)
        self.spin_presupuesto.setValue(0)
        self.spin_tiempo.setValue(0)
        self.spin_vmuseo.setValue(0)
        self.combo_multi.setCurrentIndex(0)
        self.consola_registros.clear()
        self.txt_origen.clear()
        self.coords_origen = None
        self.tiempo_disponible = 0
        self.presupuesto_disponible = 0
        self.lbl_tiempo_restante.setText("Tiempo: -")
        self.lbl_dinero_restante.setText("Presupuesto: - Bs")
        self.btn_calcular.setEnabled(True)
        self.actualizar_mapa()
        self.consola_registros.append("[Sistema] El programa ha sido restablecido a su estado inicial.")

    def on_map_clicked(self, lat, lon):
        if self.coords_origen is not None:
            return 
        self.coords_origen = (lat, lon)
        self.consola_registros.append(f"Clic en mapa: ({lat:.5f}, {lon:.5f}). Buscando dirección...")
        try:
            loc = self.geolocator.reverse(f"{lat}, {lon}")
            if loc:
                calle = loc.address.split(",")[0]
                self.txt_origen.setText(calle + ", Cbba")
            else:
                self.txt_origen.setText(f"{lat:.4f}, {lon:.4f}")
        except:
            self.txt_origen.setText(f"{lat:.4f}, {lon:.4f}")
        self.consola_registros.append(f"Origen fijado por clic interactivo.")
        self.actualizar_mapa()

    def fijar_origen(self):
        if self.coords_origen is not None:
            QMessageBox.information(self, "Aviso", "El origen ya está fijado. Si deseas cambiarlo, presiona 'Detener y Limpiar'.")
            return
        direccion = self.txt_origen.text()
        if not direccion: return
        self.consola_registros.append(f"Geolocalizando texto: {direccion}...")
        QApplication.processEvents()
        try:
            loc = self.geolocator.geocode(direccion + ", Cochabamba, Bolivia")
            if loc:
                self.coords_origen = (loc.latitude, loc.longitude)
                self.consola_registros.append(f"Origen fijado en: {loc.latitude}, {loc.longitude}")
                self.actualizar_mapa()
            else:
                QMessageBox.warning(self, "Error", "Dirección no encontrada.")
        except Exception as e:
            self.consola_registros.append(f"Error: {e}")

    def actualizar_mapa(self, ruta_activa=None):
        centro = self.coords_origen if self.coords_origen else [-17.3935, -66.1568]
        mapa = folium.Map(location=centro, zoom_start=16, tiles="CartoDB positron")
        museos_json = json.dumps(MUSEOS)

        js_injection = f"""
        <script>
        document.addEventListener('DOMContentLoaded', function() {{
            var map = null;
            for (var key in window) {{
                if (key.startsWith('map_') && window[key] instanceof L.Map) {{
                    map = window[key]; break;
                }}
            }}
            if (map) {{
                map.on('click', function(e) {{
                    window.location.href = 'pyqt://mapclick?lat=' + e.latlng.lat + '&lon=' + e.latlng.lng;
                }});
                
                window.museumMarkers = {{}};
                var museos = {museos_json};
                
                for (var nombre in museos) {{
                    var coord = museos[nombre];
                    var letra = nombre.charAt(1);
                    var iconHtml = "<div style='background-color: red; color: white; border-radius: 50%; width: 20px; height: 20px; text-align: center; font-weight: bold; font-size: 13px; line-height: 20px; border: 1px solid black; box-shadow: 1px 1px 2px rgba(0,0,0,0.5);'>" + letra + "</div>";
                    var icon = L.divIcon({{
                        className: 'custom-div-icon',
                        html: iconHtml,
                        iconSize: [20, 20],
                        iconAnchor: [10, 10]
                    }});
                    var marker = L.marker([coord[0], coord[1]], {{icon: icon}}).addTo(map);
                    marker.bindPopup(nombre);
                    window.museumMarkers[nombre] = marker;
                }}
                
                window.updateMuseumMarker = function(nombre, color) {{
                    if (window.museumMarkers[nombre]) {{
                        var markerElement = window.museumMarkers[nombre].getElement();
                        if (markerElement && markerElement.firstChild) {{
                            markerElement.firstChild.style.backgroundColor = color;
                            markerElement.firstChild.style.color = (color === 'yellow') ? 'black' : 'white';
                        }}
                    }}
                }};
                
                window.traveledLines = [];
                window.traveledLine = null;
                window.startNewTraveledLine = function(color, is_dotted) {{
                    var dash = is_dotted ? "5, 10" : "0";
                    var line = L.polyline([], {{color: color, weight: 6, opacity: 1.0, dashArray: dash}}).addTo(map);
                    window.traveledLine = line;
                    window.traveledLines.push(line);
                }};
                
                window.movingMarker = null;
                window.updateMovingMarker = function(lat, lon, color) {{
                    if (window.movingMarker == null) {{
                        window.movingMarker = L.circleMarker([lat, lon], {{
                            radius: 8, color: 'white', fillColor: color, 
                            fillOpacity: 1, weight: 2
                        }}).addTo(map);
                    }} else {{
                        window.movingMarker.setLatLng([lat, lon]);
                        window.movingMarker.setStyle({{fillColor: color}});
                    }}
                    if (window.traveledLine) {{
                        window.traveledLine.addLatLng([lat, lon]);
                    }}
                }};
                window.removeMovingMarker = function() {{
                    if (window.movingMarker) {{
                        map.removeLayer(window.movingMarker);
                        window.movingMarker = null;
                    }}
                    if (window.traveledLines) {{
                        window.traveledLines.forEach(function(line) {{
                            map.removeLayer(line);
                        }});
                        window.traveledLines = [];
                    }}
                    window.traveledLine = null;
                }};
            }}
        }});
        </script>
        """
        mapa.get_root().html.add_child(folium.Element(js_injection))

        if self.coords_origen:
            folium.Marker(location=self.coords_origen, popup="Origen", icon=folium.Icon(color='red', icon='home')).add_to(mapa)
        if ruta_activa:
            puntos_ruta = [list(self.coords_origen)] if self.coords_origen else []
            for tramo in ruta_activa['detalles_ruta']:
                geom = tramo['geometria']
                modo = tramo['modo']
                color = "green"
                dash = "5, 10" if modo == "Pie" else "0"
                folium.PolyLine(geom, color=color, weight=6, opacity=0.6, dash_array=dash).add_to(mapa)
                puntos_ruta.extend(geom)
            if puntos_ruta:
                mapa.fit_bounds(puntos_ruta, padding=[40, 40])
        mapa_path = os.path.abspath("mapa_museos.html")
        mapa.save(mapa_path)
        self.vista_web.load(QUrl.fromLocalFile(mapa_path))
        try:
            self.vista_web.loadFinished.disconnect(self.restore_checkbox_colors)
        except TypeError:
            pass
        self.vista_web.loadFinished.connect(self.restore_checkbox_colors)

    def restore_checkbox_colors(self):
        for i in range(self.lista_museos.count()):
            item = self.lista_museos.item(i)
            if item.flags() & Qt.ItemIsUserCheckable and item.checkState() == Qt.Checked:
                self.al_seleccionar_museo(item)

    def calcular_rutas(self):
        if not self.coords_origen:
            QMessageBox.warning(self, "Atención", "Fija un punto de origen (clic en mapa o texto).")
            return
        museos_seleccionados = []
        for i in range(self.lista_museos.count()):
            item = self.lista_museos.item(i)
            if (item.flags() & Qt.ItemIsUserCheckable) and item.checkState() == Qt.Checked:
                museos_seleccionados.append(item.text())
        if not museos_seleccionados: return
        self.btn_calcular.setEnabled(False)
        self.tiempo_disponible = self.spin_tiempo.value()
        self.presupuesto_disponible = self.spin_presupuesto.value()
        self.lbl_tiempo_restante.setText(f"Tiempo: {self.tiempo_disponible:.1f} min")
        self.lbl_dinero_restante.setText(f"Presupuesto: {self.presupuesto_disponible:.1f} Bs")
        self.consola_registros.clear()
        self.consola_registros.append(f"[Buscador] Buscando rutas para {len(museos_seleccionados)} museos...")
        self.hilo_buscador = AgenteBuscadorInterno(
            self.coords_origen, museos_seleccionados, self.presupuesto_disponible,
            self.tiempo_disponible, self.spin_vauto.value(), 
            self.spin_vpie.value(), self.spin_vmuseo.value()
        )
        self.hilo_buscador.progress.connect(self.consola_registros.append)
        self.hilo_buscador.finished.connect(self.on_rutas_calculadas)
        self.hilo_buscador.error.connect(lambda e: self.consola_registros.append(f"Error: {e}"))
        self.hilo_buscador.start()

    def on_rutas_calculadas(self, rutas_validas):
        self.btn_calcular.setEnabled(True)
        if not rutas_validas:
            self.consola_registros.append("¡NINGUNA ALTERNATIVA ES VÁLIDA! Falta tiempo o presupuesto_max.")
            QMessageBox.critical(self, "Ruta Imposible", "No alcanza el dinero o el tiempo para ninguna de las opciones. Modifica tus restricciones.")
            return
            
        max_museos = max(r['num_museos'] for r in rutas_validas)
        rutas_filtradas = [r for r in rutas_validas if r['num_museos'] == max_museos]
        rutas_filtradas.sort(key=lambda x: (x['costo'], x['tiempo']))
        
        self.combo_rutas.clear()
        for r in rutas_filtradas:
            texto = f"{r['nombre']} | Costo: {r['costo']:.1f} Bs | Tiempo: {r['tiempo']:.1f} min"
            item = QListWidgetItem(texto)
            item.setData(Qt.UserRole, r)
            self.combo_rutas.addItem(item)
            
        self.combo_rutas.setEnabled(True)
        self.btn_iniciar.setEnabled(True)
        self.consola_registros.append(f"¡Se encontraron {len(rutas_filtradas)} opciones viables que visitan el máximo posible de {max_museos} museos!")
        self.consola_registros.append("Selecciona una ruta de la lista y presiona Iniciar.")
    def previsualizar_ruta(self):
        item = self.combo_rutas.currentItem()
        if not item: return
        ruta_optima = item.data(Qt.UserRole)
        self.actualizar_mapa(ruta_optima)
    def iniciar_recorrido_seleccionado(self):
        item = self.combo_rutas.currentItem()
        if not item: return
        ruta_optima = item.data(Qt.UserRole)
        self.btn_calcular.setEnabled(False)
        self.btn_iniciar.setEnabled(False)
        self.combo_rutas.setEnabled(False)
        self.consola_registros.append(f"\\nOpción seleccionada: {ruta_optima['nombre']}")
        modos_str = " -> ".join(ruta_optima['modos'])
        self.consola_registros.append(f"Modos de Transporte elegidos: {modos_str}")
        self.actualizar_mapa(ruta_optima)
        self.guia = AgenteGuiaLocal(self, self.descontar_tiempo_tick, self.descontar_dinero, self.spin_vmuseo.value())
        multi = int(self.combo_multi.currentText().replace("x", ""))
        self.consola_registros.append("\\n--- INICIANDO SIMULACIÓN ANIMADA ---")
        self.transporte.iniciar_ruta(
            ruta_optima, 
            self.spin_vauto.value(), 
            self.spin_vpie.value(), 
            multi,
            self.guia.procesar_llegada
        )

    def descontar_dinero(self, cantidad, concepto):
        if cantidad > 0:
            self.presupuesto_disponible -= cantidad
            self.lbl_dinero_restante.setText(f"Presupuesto: {self.presupuesto_disponible:.1f} Bs")
            self.consola_registros.append(f"[Dinero] -{cantidad} Bs por {concepto}. (Quedan {self.presupuesto_disponible} Bs)")

    def descontar_tiempo_tick(self, minutos):
        self.tiempo_disponible -= minutos
        self.lbl_tiempo_restante.setText(f"Tiempo: {self.tiempo_disponible:.1f} min")
