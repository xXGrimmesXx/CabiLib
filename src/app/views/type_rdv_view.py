from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, 
                               QTableWidgetItem, QLabel, QPushButton, QLineEdit,
                            QComboBox, QTextEdit, QColorDialog, QHeaderView,QCheckBox)
from PySide6.QtCore import Signal
from PySide6.QtGui import QColor

from datetime import datetime,timedelta

import app.services.constantes_manager as constantes_manager

class TypeRDVView(QWidget):
    """Vue pour gérer les types de rendez-vous"""
    
    # Signaux
    type_rdv_selected: Signal = Signal(int)
    """Signal émis lors de la sélection d'un type de RDV (index de ligne)."""
    type_rdv_updated: Signal = Signal(object)
    """Signal émis lors de la mise à jour d'un type de RDV."""
    type_rdv_deleted: Signal = Signal(int)
    """Signal émis lors de la suppression d'un type de RDV (id)."""
    type_rdv_created: Signal = Signal(object)
    """Signal émis lors de la création d'un type de RDV."""
    type_rdv_deleted: Signal = Signal(int)
    """Signal émis lors de la suppression d'un type de RDV."""
    refresh: Signal = Signal()
    """Signal pour rafraîchir la vue des types de RDV."""
    
    def __init__(self) -> None:
        """
        Initialise la vue de gestion des types de rendez-vous.
        """
        super().__init__()
        self.setup_ui()
        self.types_rdv = []
        self.selected_type_rdv_id = None
    
    def setup_ui(self) -> None:
        """
        Crée et configure l'interface utilisateur pour la gestion des types de RDV.
        """
        """Création de l'interface utilisateur"""
        
        main_layout = QVBoxLayout(self)
        
        # Table des types de RDV
        self.type_rdv_table = QTableWidget()
        self.type_rdv_table.setColumnCount(8)
        self.type_rdv_table.setHorizontalHeaderLabels(["ID", "Nom", "Description", "Prix","Durée", "Localisation", "Couleur", "Groupe"])
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
        locs = constantes_manager.get_constante("LOCALISATIONS_RDV") or []
        self.localisation_input.addItems(locs)
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
        self.duree_input = QLineEdit()
        self.duree_input.setPlaceholderText("Durée en minutes")
        row3.addWidget(self.duree_input)

        row3.addWidget(QLabel("Rendez-vous de groupe"))
        self.groupe_input = QCheckBox()
        self.groupe_input.setToolTip("Cochez si ce type de rendez-vous est un rendez-vous de groupe")
        self.groupe_input.setStyleSheet("""
    QCheckBox::indicator {
        width: 20px;
        height: 20px;
    }
    QCheckBox::indicator:unchecked {
        border: 2px solid #333;
        background: #ffffff;  /* blanc */
    }
    QCheckBox::indicator:checked {
        border: 2px solid #333;
        background: #4CAF50;  /* vert vif */
    }
""")
        row3.addWidget(self.groupe_input)

        form_layout.addLayout(row3)
        
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
        
        self.clear_button = QPushButton("Effacer les champs")
        self.clear_button.clicked.connect(self._on_clear_clicked)
        buttons_layout.addWidget(self.clear_button)

        self.delete_button = QPushButton("Supprimer le type")
        self.delete_button.clicked.connect(self.on_delete_clicked)
        buttons_layout.addWidget(self.delete_button)

    def on_refresh(self):
        """Rafraîchir la vue (ex: recharger les listes déroulantes si besoin)"""
        self.localisation_input.clear()
        localisation_options = constantes_manager.get_constante("LOCALISATIONS_RDV") or []
        self.localisation_input.addItems(localisation_options)
        self.refresh.emit()
    
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
            self.type_rdv_table.setItem(row_position, 4, QTableWidgetItem((datetime(2000,1,1,0,0) + type_rdv.duree).strftime("%H:%M")))
            self.type_rdv_table.setItem(row_position, 5, QTableWidgetItem(type_rdv.localisation))
        
            self.type_rdv_table.setItem(row_position, 7, QTableWidgetItem(type_rdv.estgroupe and "Oui" or "Non"))
            
            # Couleur
            color_item = QTableWidgetItem()
            color_item.setBackground(QColor(type_rdv.couleur))
            self.type_rdv_table.setItem(row_position, 6, color_item)
        
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
        self.duree_input.setText(str(type_rdv.duree.seconds // 60))
        self.groupe_input.setChecked(type_rdv.estgroupe)
    
    def get_type_rdv_details(self):
        """Récupérer les valeurs du formulaire"""
        from app.model.typeRDV import TypeRDV
        duree_minutes = int(self.duree_input.text()) if self.duree_input.text().isdigit() else self.error_duree()
        prix = float(self.prix_input.text()) if self.prix_input.text().replace('.','',1).isdigit() else self.error_prix()
        return TypeRDV(
            id=self.selected_type_rdv_id,
            nom=self.nom_input.text(),
            description=self.description_input.toPlainText(),
            prix=float(self.prix_input.text()) if self.prix_input.text() else 0.0,
            localisation=self.localisation_input.currentText(),
            couleur=getattr(self, 'selected_color', '#FFFFFF'),
            duree=timedelta(minutes=int(self.duree_input.text())),
            estgroupe=self.groupe_input.isChecked()
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
        self.type_rdv_table.setItem(row, 5, QTableWidgetItem(type_rdv.duree))
        self.type_rdv_table.setItem(row, 7, QTableWidgetItem(type_rdv.groupe and "Oui" or "Non"))
        
        color_item = QTableWidgetItem()
        color_item.setBackground(QColor(type_rdv.couleur))
        self.type_rdv_table.setItem(row, 6, color_item)
    
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
    
    def _on_clear_clicked(self):
        """Gérer le clic sur le bouton Effacer les champs"""
        self.nom_input.clear()
        self.prix_input.clear()
        self.localisation_input.setCurrentIndex(0)
        self.description_input.clear()
        self.couleur_preview.setStyleSheet("border: 1px solid black;")
        self.type_rdv_table.clearSelection()
        self.selected_color = "#FFFFFF"
        self.duree_input.setText("")
        self.groupe_input.setChecked(False)
        self.selected_type_rdv_id = None

    def error_duree(self):
        """Afficher une erreur si la durée n'est pas valide"""
        from PySide6.QtWidgets import QMessageBox
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setText("Erreur de saisie")
        msg.setInformativeText('La durée doit être un nombre entier représentant les minutes.')
        msg.setWindowTitle("Erreur")
        msg.exec()
        return None
    
    def error_prix(self):
        """Afficher une erreur si le prix n'est pas valide"""
        from PySide6.QtWidgets import QMessageBox
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setText("Erreur de saisie")
        msg.setInformativeText('Le prix doit être un nombre valide (ex: 50.0).')
        msg.setWindowTitle("Erreur")
        msg.exec()
        return None
    
    def on_delete_clicked(self):
        """Gérer le clic sur le bouton Supprimer le type"""
        if self.selected_type_rdv_id is not None:
            self.type_rdv_deleted.emit(self.selected_type_rdv_id)
            self.selected_type_rdv_id = None
            self._on_clear_clicked()
            self.refresh.emit()

    def afficher_erreur_suppression_type_rdv_lie(self):
        """Afficher une erreur si le type de RDV est lié à des rendez-vous"""
        from PySide6.QtWidgets import QMessageBox
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setText("Erreur de suppression")
        msg.setInformativeText('Ce type de rendez-vous est lié à des rendez-vous existants et ne peut pas être supprimé.')
        msg.setWindowTitle("Erreur")
        msg.exec()