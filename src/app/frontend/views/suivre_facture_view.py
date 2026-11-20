from PySide6.QtWidgets import (QDateEdit, QPushButton, QTextEdit, QWidget, QGridLayout, QTableWidget, 
                               QTableWidgetItem, QLabel, QLineEdit,
                               QHBoxLayout, QVBoxLayout)
from PySide6.QtCore import Qt, Signal
from app.backend.model.facture import Facture
from app.backend.services.rendezVous_service import RendezVousService
from app.backend.services.patient_service import PatientService


class SuivreFactureView(QWidget):
    """VIEW - Interface graphique pour la gestion des patients"""
    
    # Signaux pour communiquer avec le Controller
    facture_selected: Signal = Signal(int)
    """Signal émis lors de la sélection d'une facture (index de ligne)."""
    facture_updated: Signal = Signal(Facture)
    """Signal émis lors de la mise à jour d'une facture."""
    ligne_facture_selected: Signal = Signal(int)
    """Signal émis lors de la sélection d'une ligne de facture (index de ligne)."""
    search_changed: Signal = Signal(str)
    """Signal émis lors d'une recherche dans la barre de recherche."""
    refresh: Signal = Signal()
    """Signal pour rafraîchir la vue des factures."""
    reediter: Signal = Signal(str)
    """Signal pour rééditer une facture (ID de la facture)."""

    def __init__(self) -> None:
        """
        Initialise la vue de suivi des factures.
        """
        super().__init__()
        self.setup_ui()
    
    def setup_ui(self) -> None:
        """
        Crée et configure l'interface utilisateur pour le suivi des factures.
        """
        """Création de l'interface utilisateur"""

        main_grid = QGridLayout(self)
        self.setLayout(main_grid)

        #Barre de recherche
        self.search_label = QLabel("Rechercher une facture:")
        self.search_input = QLineEdit()
        main_grid.addWidget(self.search_label, 0, 0)
        main_grid.addWidget(self.search_input, 0, 1)
        self.search_input.textChanged.connect(self.on_search_text_changed)

        # Table des patients
        self.facture_table = QTableWidget()
        self.facture_table.setColumnCount(6)
        self.facture_table.setHorizontalHeaderLabels(["Numéro de facture", "Patient", "Date d'émission", "Méthode de paiement","Date de paiement","Description"])
        self.facture_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.facture_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.facture_table.setSelectionMode(QTableWidget.SingleSelection)
        self.facture_table.horizontalHeader().setStretchLastSection(True)
        self.facture_table.setColumnWidth(0, 150)
        self.facture_table.setColumnWidth(1, 150)
        self.facture_table.setColumnWidth(2, 120)
        self.facture_table.setColumnWidth(3, 150)
        self.facture_table.cellClicked.connect(lambda row, col: self.facture_selected.emit(row))
        self.facture_table.setSortingEnabled(True)
        main_grid.addWidget(self.facture_table, 1, 0, 1, 2)
        main_grid.setRowStretch(1, 2)  # La table prend 2x plus de place que les autres lignes

        self.lignesFacture = QTableWidget()
        self.lignesFacture.setColumnCount(3)
        self.lignesFacture.setHorizontalHeaderLabels(["Numéro de facture", "Date du rendez-vous", "Montant"])
        self.lignesFacture.setEditTriggers(QTableWidget.NoEditTriggers)
        self.lignesFacture.setSelectionBehavior(QTableWidget.SelectRows)
        self.lignesFacture.setSelectionMode(QTableWidget.SingleSelection)
        self.lignesFacture.horizontalHeader().setStretchLastSection(False)
        self.lignesFacture.setColumnWidth(0, 150)
        self.lignesFacture.setColumnWidth(1, 150)
        main_grid.addWidget(self.lignesFacture, 2, 0, 1, 1)
        main_grid.setRowStretch(2, 1)  # La table prend 1x plus de place que les autres lignes

        facture_detail = QVBoxLayout()
        
        main_grid.addLayout(facture_detail, 2, 1, 1, 2)

        titre = QLabel("Détails de la facture")
        titre.setAlignment(Qt.AlignCenter)
        titre.setStyleSheet("font-size: 15pt; font-weight: bold;")
        facture_detail.addWidget(titre)

        # Dates et moyens de paiment de la facture
        details_paiement = QHBoxLayout()
        facture_detail.addLayout(details_paiement)
        details_paiement.addWidget(QLabel("Méthode de paiement:"))
        self.methode_paiement_input = QLineEdit()
        details_paiement.addWidget(self.methode_paiement_input)
        details_paiement.addWidget(QLabel("Date de paiement:"))
        self.date_paiement_input = QDateEdit()
        self.date_paiement_input.setCalendarPopup(True)
        details_paiement.addWidget(self.date_paiement_input)


        #description de la facture
        description_layout = QHBoxLayout()
        facture_detail.addLayout(description_layout)
        description_layout.addWidget(QLabel("Description:"))
        self.description_input = QTextEdit()
        description_layout.addWidget(self.description_input)

        #boutons d'enregistrement et de réedition de la facture
        buttons_layout = QHBoxLayout()
        facture_detail.addLayout(buttons_layout)
        self.enregistrer_button = QPushButton("Enregistrer")
        self.enregistrer_button.clicked.connect(self.on_enregistrer_clicked)
        buttons_layout.addWidget(self.enregistrer_button)
        self.reediter_button = QPushButton("Rééditer")
        self.reediter_button.clicked.connect(self.on_reediter_clicked)
        buttons_layout.addWidget(self.reediter_button)

        
        


    def on_refresh(self) -> None:
        """
        Rafraîchit la vue (recharge les factures).
        """
        """Rafraîchir la vue (recharger les factures)"""
        self.refresh.emit()
    
    def on_search_text_changed(self, text: str) -> None:
        """
        Émet le signal de changement de recherche.
        Args:
            text (str): Texte de recherche saisi.
        """
        """Émettre le signal de changement de recherche"""
        self.search_changed.emit(text)

    def filter_rows(self, search_text: str) -> None:
        """
        Filtre les lignes selon le texte de recherche.
        Args:
            search_text (str): Texte de recherche à filtrer.
        """
        """Filtrer les lignes selon le texte de recherche"""
        for row in range(self.facture_table.rowCount()):
            match = False
            for column in range(self.facture_table.columnCount()):
                item = self.facture_table.item(row, column)
                if item and search_text.lower() in item.text().lower():
                    match = True
                    break
            self.facture_table.setRowHidden(row, not match)

    def load_factures(self, factures: list) -> None:
        """
        Charge les factures dans la table.
        Args:
            factures (list): Liste des factures à afficher.
        """
        """Charger les factures dans la table"""
        self.facture_table.setRowCount(0)  # Vider la table avant de charger

        for facture in factures:
            row_position = self.facture_table.rowCount()
            self.facture_table.insertRow(row_position)

            self.facture_table.setItem(row_position, 0, QTableWidgetItem(facture.id))

            patient_id_item = QTableWidgetItem()
            patient_id_item.setData(Qt.DisplayRole, PatientService.get_patient_by_id(facture.patient_id).nom_complet())
            self.facture_table.setItem(row_position, 1, patient_id_item)
            
            self.facture_table.setItem(row_position, 2, QTableWidgetItem(facture.date_emission.strftime("%Y-%m-%d")))
            self.facture_table.setItem(row_position, 3, QTableWidgetItem(facture.statut))
            date_paiement_str = facture.date_paiement.strftime("%Y-%m-%d") if facture.date_paiement else "N/A"
            self.facture_table.setItem(row_position, 4, QTableWidgetItem(date_paiement_str))
            self.facture_table.setItem(row_position, 5, QTableWidgetItem(facture.description))

    def display_facture_details(self, facture, lignes_facture) -> None:
        """
        Affiche les détails d'une facture sélectionnée.
        Args:
            facture: Facture sélectionnée.
            lignes_facture: Lignes associées à la facture.
        """
        """Afficher les détails d'une facture sélectionnée"""
        # Mettre à jour les champs de la facture
        # (À implémenter si nécessaire)

        # Charger les lignes de facture associées
        self.lignesFacture.setRowCount(0)  # Vider la table avant de charger

        for ligne in lignes_facture:
            row_position = self.lignesFacture.rowCount()
            self.lignesFacture.insertRow(row_position)

            self.lignesFacture.setItem(row_position, 0, QTableWidgetItem(ligne.idFacture))
            self.lignesFacture.setItem(row_position, 1, QTableWidgetItem(RendezVousService.get_rendezvous_by_id(ligne.idRendezVous).date.strftime("%Y-%m-%d")))
            self.lignesFacture.setItem(row_position, 2, QTableWidgetItem(str(ligne.montant_facture)))

    def on_enregistrer_clicked(self) -> None:
        """
        Émet le signal de mise à jour de la facture avec les nouvelles informations.
        """
        """Émettre le signal de mise à jour de la facture avec les nouvelles informations"""
        # Récupérer les informations mises à jour
        updated_facture = Facture(
            id=self.facture_table.item(self.facture_table.currentRow(), 0).text(),
            patient_id=None,
            date_emission=None,
            statut=self.methode_paiement_input.text(),
            date_paiement=self.date_paiement_input.date().toPython(),
            description=self.description_input.toPlainText()
        )
        self.facture_updated.emit(updated_facture)

    def on_reediter_clicked(self) -> None:
        """
        Émet le signal pour rééditer la facture sélectionnée.
        """
        """Émettre le signal pour rééditer la facture sélectionnée"""
        print(f"Réédition en vue")
        self.reediter.emit(self.facture_table.item(self.facture_table.currentRow(), 0).text())
        print("fin de l'émission du signal")