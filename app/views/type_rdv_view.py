from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, 
                               QTableWidgetItem, QLabel, QPushButton, QLineEdit,
                            QComboBox, QTextEdit, QColorDialog, QHeaderView,QCheckBox)
from PySide6.QtCore import Signal
from PySide6.QtGui import QColor

import utils.constantes_manager as constantes_manager

class TypeRDVView(QWidget):
    """Vue pour gérer les types de rendez-vous"""
    
    # Signaux
    type_rdv_selected = Signal(int)  # row index
    type_rdv_updated = Signal(object)
    type_rdv_deleted = Signal(int)  # type_rdv id
    type_rdv_created = Signal(object)
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.types_rdv = []
        self.selected_type_rdv_id = None
    
    def setup_ui(self):
        """Création de l'interface utilisateur"""
        
        main_layout = QVBoxLayout(self)
        
        # Table des types de RDV
        self.type_rdv_table = QTableWidget()
        self.type_rdv_table.setColumnCount(6)
        self.type_rdv_table.setHorizontalHeaderLabels(["ID", "Nom", "Description", "Prix", "Localisation", "Couleur"])
        self.type_rdv_table.setColumnHidden(0, True)  # Cacher la colonne ID
        self.type_rdv_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.type_rdv_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.type_rdv_table.setSelectionMode(QTableWidget.NoSelection)
        self.type_rdv_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.type_rdv_table.cellClicked.connect(lambda row, col: self.type_rdv_selected.emit(row))
        self.type_rdv_table.setSortingEnabled(True)
        main_layout.addWidget(self.type_rdv_table)
        
        # Formulaire de détails
        form_layout = QVBoxLayout()
        main_layout.addLayout(form_layout)
        
        # Ligne 1 : Nom et Prix
        row1 = QHBoxLayout()
        row1.addWidget(QLabel("Nom :"))
        self.nom_input = QLineEdit()
        row1.addWidget(self.nom_input)
        row1.addWidget(QLabel("Prix (€) :"))
        self.prix_input = QLineEdit()
        row1.addWidget(self.prix_input)
        form_layout.addLayout(row1)
        
        # Ligne 2 : Localisation et Couleur
        row2 = QHBoxLayout()
        row2.addWidget(QLabel("Localisation :"))
        self.localisation_input = QComboBox()
        self.localisation_input.addItems(["Cabinet", "A domicile", "Téléconsultation"])
        self.localisation_input.setEditable(True)
        row2.addWidget(self.localisation_input)
        row2.addWidget(QLabel("Couleur :"))
        self.couleur_input = QPushButton("Choisir couleur")
        self.couleur_input.clicked.connect(self.choose_color)
        self.couleur_preview = QLabel("     ")
        self.couleur_preview.setStyleSheet("border: 1px solid black;")
        row2.addWidget(self.couleur_preview)
        row2.addWidget(self.couleur_input)
        form_layout.addLayout(row2)

        row3 = QHBoxLayout()
        row3.addWidget(QLabel("Durée"))
        self.duree_input = QComboBox()
        # DUREES_RDV est une liste de chaînes "HH:MM"
        durees = constantes_manager.get_constante("DUREES_RDV")
        self.duree_input.addItems(durees)
        row3.addWidget(self.duree_input)

        row3.addWidget(QLabel("Rendez-vous de groupe"))
        self.groupe_input = QCheckBox()
        row3.addWidget(self.groupe_input)
        
        # Description
        form_layout.addWidget(QLabel("Description :"))
        self.description_input = QTextEdit()
        form_layout.addWidget(self.description_input)
        
        # Boutons d'action
        buttons_layout = QHBoxLayout()
        form_layout.addLayout(buttons_layout)
        
        self.validate_button = QPushButton("Valider les modifications")
        self.validate_button.clicked.connect(self._on_validate_clicked)
        buttons_layout.addWidget(self.validate_button)
        
        self.creer_button = QPushButton("Créer un nouveau type")
        self.creer_button.clicked.connect(self._on_creer_clicked)
        buttons_layout.addWidget(self.creer_button)
        
        self.supprimer_button = QPushButton("Supprimer le type")
        self.supprimer_button.clicked.connect(self._on_supprimer_clicked)
        buttons_layout.addWidget(self.supprimer_button)
        
        self.clear_button = QPushButton("Effacer les champs")
        self.clear_button.clicked.connect(self._on_clear_clicked)
        buttons_layout.addWidget(self.clear_button)
    
    def choose_color(self):
        """Ouvrir le sélecteur de couleur"""
        color = QColorDialog.getColor()
        if color.isValid():
            self.couleur_preview.setStyleSheet(f"background-color: {color.name()}; border: 1px solid black;")
            self.selected_color = color.name()
    
    def load_types_rdv(self, types_rdv_data):
        """Charger les données des types de RDV dans la table"""
        self.type_rdv_table.setSortingEnabled(False)
        self.type_rdv_table.setRowCount(0)
        for type_rdv in types_rdv_data:
            row_position = self.type_rdv_table.rowCount()
            self.type_rdv_table.insertRow(row_position)
            
            self.type_rdv_table.setItem(row_position, 0, QTableWidgetItem(str(type_rdv.id)))
            self.type_rdv_table.setItem(row_position, 1, QTableWidgetItem(type_rdv.nom))
            self.type_rdv_table.setItem(row_position, 2, QTableWidgetItem(type_rdv.description))
            self.type_rdv_table.setItem(row_position, 3, QTableWidgetItem(f"{type_rdv.prix:.2f} €"))
            self.type_rdv_table.setItem(row_position, 4, QTableWidgetItem(type_rdv.localisation))
            
            # Couleur
            color_item = QTableWidgetItem()
            color_item.setBackground(QColor(type_rdv.couleur))
            self.type_rdv_table.setItem(row_position, 5, color_item)
        
        self.type_rdv_table.setSortingEnabled(True)
        self.type_rdv_table.resizeColumnsToContents()
    
    def display_type_rdv_details(self, type_rdv):
        """Afficher les détails d'un type de RDV dans le formulaire"""
        self.selected_type_rdv_id = type_rdv.id
        self.nom_input.setText(type_rdv.nom)
        self.prix_input.setText(str(type_rdv.prix))
        self.localisation_input.setCurrentText(type_rdv.localisation)
        self.description_input.setText(type_rdv.description)
        self.couleur_preview.setStyleSheet(f"background-color: {type_rdv.couleur}; border: 1px solid black;")
        self.selected_color = type_rdv.couleur
    
    def get_type_rdv_details(self):
        """Récupérer les valeurs du formulaire"""
        from app.model.typeRDV import TypeRDV
        return TypeRDV(
            id=self.selected_type_rdv_id,
            nom=self.nom_input.text(),
            description=self.description_input.toPlainText(),
            prix=float(self.prix_input.text()) if self.prix_input.text() else 0.0,
            localisation=self.localisation_input.currentText(),
            couleur=getattr(self, 'selected_color', '#FFFFFF')
        )
    
    def get_selected_row(self):
        """Récupérer la ligne sélectionnée"""
        selected_items = self.type_rdv_table.selectedItems()
        if selected_items:
            return selected_items[0].row()
        return None
    
    def update_table_row(self, row, type_rdv):
        """Mettre à jour une ligne dans la table"""
        self.type_rdv_table.setItem(row, 1, QTableWidgetItem(type_rdv.nom))
        self.type_rdv_table.setItem(row, 2, QTableWidgetItem(type_rdv.description))
        self.type_rdv_table.setItem(row, 3, QTableWidgetItem(f"{type_rdv.prix:.2f} €"))
        self.type_rdv_table.setItem(row, 4, QTableWidgetItem(type_rdv.localisation))
        
        color_item = QTableWidgetItem()
        color_item.setBackground(QColor(type_rdv.couleur))
        self.type_rdv_table.setItem(row, 5, color_item)
    
    def _on_validate_clicked(self):
        """Gérer le clic sur le bouton Valider"""
        updated_type_rdv = self.get_type_rdv_details()
        self.type_rdv_updated.emit(updated_type_rdv)
    
    def _on_creer_clicked(self):
        """Gérer le clic sur le bouton Créer un nouveau type"""
        type_rdv = self.get_type_rdv_details()
        self.type_rdv_created.emit(type_rdv)
        self.type_rdv_table.clearSelection()
        self._on_clear_clicked()
    
    def _on_supprimer_clicked(self):
        """Gérer le clic sur le bouton Supprimer le type"""
        selected_row = self.get_selected_row()
        if selected_row is not None:
            type_rdv_id = int(self.type_rdv_table.item(selected_row, 0).text())
            self.type_rdv_deleted.emit(type_rdv_id)
            self.type_rdv_table.clearSelection()
            self._on_clear_clicked()
    
    def _on_clear_clicked(self):
        """Gérer le clic sur le bouton Effacer les champs"""
        self.nom_input.clear()
        self.prix_input.clear()
        self.localisation_input.setCurrentIndex(0)
        self.description_input.clear()
        self.couleur_preview.setStyleSheet("border: 1px solid black;")
        self.type_rdv_table.clearSelection()
        self.selected_type_rdv_id = None