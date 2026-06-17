import networkx as nx
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas


class VentanaGrafo(QMainWindow):
    def __init__(self, ruta_optima):
        super().__init__()

        self.setWindowTitle("Grafo de Ruta de Museos")

        self.detalles = ruta_optima.get("geometrias", [])
        self.grafo = nx.DiGraph()

        self.init_ui()
        self.construir_grafo()
        self.dibujar()

    
    def init_ui(self):
        self.widget = QWidget()
        self.layout = QVBoxLayout()

        self.fig, self.ax = plt.subplots()
        self.canvas = FigureCanvas(self.fig)

        self.layout.addWidget(self.canvas)
        self.widget.setLayout(self.layout)
        self.setCentralWidget(self.widget)

    
    def construir_grafo(self):
        self.grafo.clear()

        if not self.detalles:
            print("No hay geometrias")
            return

        for tramo in self.detalles:
            origen = tramo.get("origen")
            destino = tramo.get("destino")

            if not origen or not destino:
                continue

            origen = str(origen)
            destino = str(destino)

            modo = tramo.get("modo", "?")
            distancia = tramo.get("distancia", 0)
            tiempo = tramo.get("tiempo", 0)
            costo = tramo.get("costo", 0)

            label = (
                f"{modo}\n"
                f"{distancia:.2f} km\n"
                f"{tiempo:.1f} min\n"
                f"Bs {costo:.2f}"
            )

            self.grafo.add_edge(origen, destino, label=label)

    
    def dibujar(self):
        self.ax.clear()

        if self.grafo.number_of_nodes() == 0:
            self.ax.set_title("No hay datos de ruta")
            self.canvas.draw()
            return

        pos = nx.spring_layout(self.grafo)

        nx.draw_networkx_nodes(self.grafo, pos, node_size=2000, node_color="lightblue", ax=self.ax)
        nx.draw_networkx_labels(self.grafo, pos, font_size=8, ax=self.ax)
        nx.draw_networkx_edges(self.grafo, pos, arrowstyle="->", arrowsize=20, ax=self.ax)

        edge_labels = nx.get_edge_attributes(self.grafo, "label")
        nx.draw_networkx_edge_labels(self.grafo, pos, edge_labels=edge_labels, font_size=7, ax=self.ax)

        self.ax.set_title("Ruta completa del simulador")
        self.ax.axis("off")

        self.canvas.draw()
