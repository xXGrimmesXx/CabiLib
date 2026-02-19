from datetime import datetime
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QToolTip
from PySide6.QtGui import QCursor
from PySide6.QtCore import Qt, QRect, QPoint
from app.widgetPersonalise.separator import Separator

import pyqtgraph as pg

class StatistiquesView(QWidget):
    def __init__(self):
        super().__init__()
        self.ordre_mois = [i for i in range(1, 13)]
        self.last_hovered_point = None
        self.init_UI()

    def init_UI(self):
        """Initialise l'interface utilisateur."""

        layout = QVBoxLayout(self)
        
        titre_redevance = QLabel("Statistiques")
        titre_redevance.setStyleSheet("font-size: 18pt; font-weight: bold;")
        titre_redevance.setAlignment(Qt.AlignCenter)
        titre_redevance.setContentsMargins(0, 20, 0, 20)
        layout.addWidget(titre_redevance)
        layout.addSpacing(20)  # Espacement entre le titre et les montants


        # montant mois et année en cours
        main_numbber_layout = QHBoxLayout()
        layout.addLayout(main_numbber_layout)

        mois_layout = QVBoxLayout()
        main_numbber_layout.addLayout(mois_layout)
        main_numbber_layout.addWidget(Separator(Qt.Vertical))

        année_layout = QVBoxLayout()
        main_numbber_layout.addLayout(année_layout)

        montant_mois = QLabel(f"Montant du mois de {month_to_text(datetime.now().strftime('%m'))}")
        montant_mois.setAlignment(Qt.AlignCenter)
        mois_layout.addWidget(montant_mois)

        self.montant_mois_value = QLabel("")
        self.montant_mois_value.setAlignment(Qt.AlignCenter)
        self.montant_mois_value.setStyleSheet("font-size: 16pt; font-weight: bold;")
        mois_layout.addWidget(self.montant_mois_value)

        montant_année = QLabel("Montant de l'année :")
        montant_année.setAlignment(Qt.AlignCenter)
        année_layout.addWidget(montant_année)

        self.montant_année_value = QLabel("")
        self.montant_année_value.setAlignment(Qt.AlignCenter)
        self.montant_année_value.setStyleSheet("font-size: 16pt; font-weight: bold;")
        année_layout.addWidget(self.montant_année_value)


        # graph de l'evolution du chiffre d'affaire sur les 12 derniers mois
        self.historique_graph = pg.PlotWidget()

        self.historique_graph.setBackground("w")
        self.pen = pg.mkPen(color=(255, 0, 0))
        self.pen.setWidth(2)
        self.historique_graph.setTitle("Historique du chiffre d'affaire", color="b", size="20pt")
        styles = {"color": "black", "font-size": "18px", "font-weight": "bold"}
        self.historique_graph.setLabel("left", "Chiffre d'affaire (€)", **styles)
        self.historique_graph.setLabel("bottom", "Mois", **styles)
        self.historique_graph.addLegend()
        self.historique_graph.showGrid(x=True, y=True)
        
        self.CA = [0 for _ in range(12)]

        self.historique_graph_line = self.historique_graph.plot(self.ordre_mois, self.CA, pen=self.pen)

        self.historique_graph_scatter = pg.ScatterPlotItem(self.ordre_mois, self.CA, hoverable=True, hoverSize=15, hoverPen=pg.mkPen('b'), hoverBrush=pg.mkBrush('r'), size=10, pen=pg.mkPen('b'), brush=pg.mkBrush('r'), tip=None)
        self.historique_graph.addItem(self.historique_graph_scatter)
        self.historique_graph_scatter.sigHovered.connect(self.show_tooltip)
        
        layout.addWidget(self.historique_graph)
        layout.addStretch()  # Pousse les éléments vers le haut

    def show_tooltip(self, scatter, points):
        """Gère l'affichage de la bulle d'info lors du survol."""
        print("Hover event triggered")
        if points is not None and len(points) > 0:
            print("Points hover:", points)
            # On récupère le premier point sous le curseur
            point = points[0]
            if point == self.last_hovered_point:
                return
                
            self.last_hovered_point = point
            label = point.data()  # Récupère l'étiquette définie dans addPoints
            pos = point.pos()     # Récupère les coordonnées x, y
            
            # Formatage du texte (supporte le HTML de base)
            tooltip_text = (
                f"<div style='background-color: #2b2b2b; color: white; padding: 5px;'>"
                f"<b>{label}</b></div>"
            )
            
            # Affichage à la position globale de la souris
            mouse_pos = QCursor.pos()+QPoint(10, 10)  # Décalage pour éviter de couvrir le point
            QToolTip.showText(mouse_pos, tooltip_text, self.historique_graph, QRect(), 100000)
        else:
            # Cache la bulle si la souris quitte le point
            self.last_hovered_point = None
            QToolTip.hideText()

    def update_montants(self, montant_mois: float, montant_année: float):
        """Met à jour les montants affichés pour le mois et l'année."""
        self.montant_mois_value.setText(f"{montant_mois:.2f} €")
        self.montant_année_value.setText(f"{montant_année:.2f} €")

    def update_graph(self, mois: list[int], CA: list[float]):
        # Sécurisation des données
        x_data = mois
        y_data = CA
        labels = [f"{month_to_text(str(m).zfill(2))} : {v:.2f} €" for m, v in zip(x_data, y_data)]

        # Mise à jour des deux éléments séparément
        print("Updating graph with data:", list(zip(self.ordre_mois, y_data)))
        self.historique_graph_line.setData(self.ordre_mois, y_data)
        self.historique_graph_scatter.setData(self.ordre_mois, y_data, data=labels)

        # Ajustement de l'axe Y
        self.historique_graph.setYRange(0, max(y_data) * 1.1)
        
        # Mise à jour des ticks de l'axe X
        ax = self.historique_graph.getAxis("bottom")
        month_labels = [month_to_text(str(m).zfill(2)) for m in x_data]
        ax.setTicks([list(zip(self.ordre_mois, month_labels))])
        

def month_to_text(month_number: str) -> str:
    """Convertit un numéro de mois en son nom en français."""
    months = {
        "01": "Janvier",
        "02": "Février",
        "03": "Mars",
        "04": "Avril",
        "05": "Mai",
        "06": "Juin",
        "07": "Juillet",
        "08": "Août",
        "09": "Septembre",
        "10": "Octobre",
        "11": "Novembre",
        "12": "Décembre"
    }
    return months.get(month_number, "")
