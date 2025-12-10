from PySide6.QtWidgets import (QMainWindow, QWidget, QGridLayout, QTableWidget, 
                               QTableWidgetItem, QLabel, QPushButton, QLineEdit,QComboBox,QDateEdit, QTextEdit, QCompleter)
from PySide6.QtCore import Qt, Signal, QStringListModel

from app.model.patient import Patient
from app.utils import constantes_manager
import datetime


class PatientView(QWidget):
    """VIEW - Interface graphique pour la gestion des patients"""
    
    # Signaux pour communiquer avec le Controller
    patient_selected: Signal = Signal(int)
    """Signal émis lors de la sélection d'un patient (index de ligne)."""
    patient_updated: Signal = Signal(Patient)
    """Signal émis lors de la mise à jour d'un patient."""
    patient_deleted: Signal = Signal(int)
    """Signal émis lors de la suppression d'un patient (id)."""
    patient_created: Signal = Signal(Patient)
    """Signal émis lors de la création d'un patient."""
    search_changed: Signal = Signal(str)
    """Signal émis lors d'une recherche dans la barre de recherche."""
    refresh: Signal = Signal()
    """Signal pour rafraîchir la vue des patients."""
    
    def __init__(self) -> None:
        """
        Initialise la vue de gestion des patients.
        """
        super().__init__()
        self.setup_ui()
        self.patients: list[Patient] = []
        self.selected_patient_id : int = None
    
    def setup_ui(self) -> None:
        """
        Crée et configure l'interface utilisateur pour la gestion des patients.
        """
        """Création de l'interface utilisateur"""
        
        # Layout principal
        main_grid = QGridLayout(self)
        
        # Ajouter des espacements
        
        # Définir les proportions des colonnes : 50% / 50%
        main_grid.setColumnStretch(0, 1)  # Colonne 0 = 50%
        main_grid.setColumnStretch(1, 1)  # Colonne 1 = 50%
        
        # Barre de recherche
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Rechercher un patient...")
        self.search_bar.textEdited.connect(self.search_changed.emit)
        main_grid.addWidget(self.search_bar, 0, 0)
        
        # Table des patients
        self.patient_table = QTableWidget()
        self.patient_table.setColumnCount(11)
        self.patient_table.setHorizontalHeaderLabels(["ID", "Nom", "Prenom", "Age","Niveau scolaire","Ecole", "Date de Naissance", "Ville", "Téléphone", "Email","Etat du suivi"])
        self.patient_table.setColumnHidden(0, True)  # Cacher la colonne ID
        self.patient_table.setColumnWidth(3,50)
        self.patient_table.setColumnWidth(5,150)
        self.patient_table.setColumnWidth(9,300)
        self.patient_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.patient_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.patient_table.setSelectionMode(QTableWidget.SingleSelection)
        self.patient_table.horizontalHeader().setStretchLastSection(True)
        self.patient_table.cellClicked.connect(lambda row, col: self.patient_selected.emit(row))
        self.patient_table.setSortingEnabled(True)
        main_grid.addWidget(self.patient_table, 1, 0, 1, 2)
        main_grid.setRowStretch(1, 2)  # La table prend 2x plus de place que les autres lignes
        
        # Détails du patient - sur la moitié gauche
        from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout
        detail_hbox = QHBoxLayout()
        main_grid.addLayout(detail_hbox, 2, 0, 1, 2)

        # Partie gauche : infos patient (VBox)
        detail_vbox = QVBoxLayout()
        detail_hbox.addLayout(detail_vbox, 3)

        # Partie droite : description (VBox)
        desc_vbox = QVBoxLayout()
        detail_hbox.addLayout(desc_vbox, 2)

        # Infos patient (gauche)
        row1 = QHBoxLayout()
        row1.addWidget(QLabel("Nom :"))
        self.name_input = QLineEdit(); self.name_input.setMaximumWidth(150)
        row1.addWidget(self.name_input)
        row1.addWidget(QLabel("Prénom :"))
        self.prenom_input = QLineEdit(); self.prenom_input.setMaximumWidth(150)
        row1.addWidget(self.prenom_input)
        row1.addWidget(QLabel("Age :"))
        self.age_input = QLineEdit(); self.age_input.setMaximumWidth(80)
        row1.addWidget(self.age_input)
        detail_vbox.addLayout(row1)

        row2 = QHBoxLayout()
        row2.addWidget(QLabel("Sexe :"))
        self.sexe_input = QComboBox(); self.sexe_input.addItems(["M", "F", "NB"]); self.sexe_input.setMaximumWidth(100)
        row2.addWidget(self.sexe_input)
        row2.addWidget(QLabel("Date de Naissance :"))
        self.date_naissance_input = QDateEdit(); self.date_naissance_input.setCalendarPopup(True); self.date_naissance_input.setDisplayFormat("dd-MM-yyyy"); self.date_naissance_input.setMaximumWidth(150)
        row2.addWidget(self.date_naissance_input)
        detail_vbox.addLayout(row2)

        row3 = QHBoxLayout()
        row3.addWidget(QLabel("Adresse :"))
        self.adresse_input = QLineEdit()
        row3.addWidget(self.adresse_input)
        row3.addWidget(QLabel("Ville :"))
        self.ville_input = QLineEdit()
        row3.addWidget(self.ville_input)
        detail_vbox.addLayout(row3)

        # Ligne 4 : Email
        row4 = QHBoxLayout()
        row4.addWidget(QLabel("Email :"))
        self.email_input = QLineEdit(); self.email_input.setPlaceholderText("exemple@email.com")
        row4.addWidget(self.email_input)
        detail_vbox.addLayout(row4)

        row5 = QHBoxLayout()
        self.telephone1_label = QLabel("Téléphone 1 :")
        row5.addWidget(self.telephone1_label)
        type_tel_options = constantes_manager.get_constante("TYPE_TELEPHONE_OPTIONS")
        self.type_telephone1_input = QComboBox(); self.type_telephone1_input.setEditable(True); self.type_telephone1_input.addItems(type_tel_options); self.type_telephone1_input.setMaximumWidth(100)
        self.completer_type_telephone1 = QCompleter(type_tel_options); self.completer_type_telephone1.setCaseSensitivity(Qt.CaseInsensitive)
        self.type_telephone1_input.setCompleter(self.completer_type_telephone1)
        row5.addWidget(self.type_telephone1_input)
        self.telephone1_input = QLineEdit(); self.telephone1_input.setPlaceholderText("Ex: 06 12 34 56 78"); self.telephone1_input.setMaximumWidth(100)
        row5.addWidget(self.telephone1_input)
        self.telephone2_label = QLabel("Téléphone 2 :")
        row5.addWidget(self.telephone2_label)
        self.type_telephone2_input = QComboBox(); self.type_telephone2_input.setEditable(True); self.type_telephone2_input.addItems(type_tel_options); self.type_telephone2_input.setMaximumWidth(100)
        self.completer_type_telephone2 = QCompleter(type_tel_options); self.completer_type_telephone2.setCaseSensitivity(Qt.CaseInsensitive); self.completer_type_telephone2.setFilterMode(Qt.MatchContains)
        self.type_telephone2_input.setCompleter(self.completer_type_telephone2)
        row5.addWidget(self.type_telephone2_input)
        self.telephone2_input = QLineEdit(); self.telephone2_input.setPlaceholderText("Ex: 06 12 34 56 78"); self.telephone2_input.setMaximumWidth(100)
        row5.addWidget(self.telephone2_input)
        detail_vbox.addLayout(row5)

        # Ligne 6 : Niveau scolaire, Ecole
        row6 = QHBoxLayout()
        row6.addWidget(QLabel("Niveau scolaire :"))
        niveau_options = constantes_manager.get_constante("NIVEAU_SCOLAIRE_OPTIONS")
        self.niveau_input = QComboBox(); self.niveau_input.setEditable(True); self.niveau_input.addItems(niveau_options)
        self.completer_niveau = QCompleter(niveau_options); self.completer_niveau.setCaseSensitivity(Qt.CaseInsensitive); self.completer_niveau.setFilterMode(Qt.MatchContains)
        self.niveau_input.setCompleter(self.completer_niveau)
        row6.addWidget(self.niveau_input)
        row6.addWidget(QLabel("École :"))
        self.ecole_input = QLineEdit()
        row6.addWidget(self.ecole_input)
        detail_vbox.addLayout(row6)

        # Ligne 7 : Aménagement, Etat du suivi
        row7 = QHBoxLayout()
        row7.addWidget(QLabel("Aménagement :"))
        amenagement_options = constantes_manager.get_constante("AMENAGEMENTS_OPTIONS")
        self.amenagement_input = QComboBox(); self.amenagement_input.addItems(amenagement_options); self.amenagement_input.setEditable(True)
        self.completer_amenagement = QCompleter(amenagement_options); self.completer_amenagement.setCaseSensitivity(Qt.CaseInsensitive); self.completer_amenagement.setFilterMode(Qt.MatchContains)
        self.amenagement_input.setCompleter(self.completer_amenagement)
        row7.addWidget(self.amenagement_input)

        row7.addWidget(QLabel("État du suivi :"))
        etat_suivi_options = constantes_manager.get_constante("ETAT_SUIVI_OPTIONS")
        self.etat_suivi_input = QComboBox(); self.etat_suivi_input.addItems(etat_suivi_options); self.etat_suivi_input.setEditable(True)
        self.completer_etat_suivi = QCompleter(etat_suivi_options); self.completer_etat_suivi.setCaseSensitivity(Qt.CaseInsensitive); self.completer_etat_suivi.setFilterMode(Qt.MatchContains)
        self.etat_suivi_input.setCompleter(self.completer_etat_suivi)
        row7.addWidget(self.etat_suivi_input)
        detail_vbox.addLayout(row7)

        # Description (droite)
        desc_vbox.addWidget(QLabel("Description :"))
        self.description_input = QTextEdit()
        desc_vbox.addWidget(self.description_input)

        button_hbox = QHBoxLayout()
        detail_vbox.addLayout(button_hbox)
        # Bouton valider (sous les infos)
        self.validate_button = QPushButton("Valider les modifications")
        self.validate_button.clicked.connect(self._on_validate_clicked)
        button_hbox.addWidget(self.validate_button, alignment=Qt.AlignCenter)

        self.creer_button = QPushButton("Créer un nouveau patient")
        button_hbox.addWidget(self.creer_button, alignment=Qt.AlignCenter)
        self.creer_button.clicked.connect(self._on_creer_clicked)

        self.supprimer_button = QPushButton("Supprimer le patient")
        button_hbox.addWidget(self.supprimer_button, alignment=Qt.AlignCenter)
        self.supprimer_button.clicked.connect(self._on_supprimer_clicked)

        self.clear_button = QPushButton("Effacer les champs")
        button_hbox.addWidget(self.clear_button, alignment=Qt.AlignCenter)
        self.clear_button.clicked.connect(self._on_clear_clicked)
    
    def on_refresh(self):
        """Rafraîchir la vue (ex: recharger les listes déroulantes si besoin)"""
        self.niveau_input.clear()
        niveau_options = constantes_manager.get_constante("NIVEAU_SCOLAIRE_OPTIONS")
        self.niveau_input.addItems(niveau_options)
        self.completer_niveau.setModel(QStringListModel(niveau_options))

        self.type_telephone1_input.clear()
        type_tel_options = constantes_manager.get_constante("TYPE_TELEPHONE_OPTIONS")
        self.type_telephone1_input.addItems(type_tel_options)
        self.completer_type_telephone1.setModel(QStringListModel(type_tel_options))

        self.type_telephone2_input.clear()
        self.type_telephone2_input.addItems(type_tel_options)
        self.completer_type_telephone2.setModel(QStringListModel(type_tel_options))

        self.amenagement_input.clear()
        amenagement_options = constantes_manager.get_constante("AMENAGEMENTS_OPTIONS")
        self.amenagement_input.addItems(amenagement_options)
        self.completer_amenagement.setModel(QStringListModel(amenagement_options))

        self.etat_suivi_input.clear()
        etat_suivi_options = constantes_manager.get_constante("ETAT_SUIVI_OPTIONS")
        self.etat_suivi_input.addItems(etat_suivi_options)
        self.completer_etat_suivi.setModel(QStringListModel(etat_suivi_options))

        self.refresh.emit()


    def load_patients(self, patients_data):
        """Charger les données des patients dans la table
        
        Args:
            patients_data: Liste de Patient
        """
        self.patient_table.setSortingEnabled(False)  # Désactiver le tri pendant l'insertion
        self.patient_table.setRowCount(0)
        for patient in patients_data:
            row_position = self.patient_table.rowCount()
            self.patient_table.insertRow(row_position)
    
            self.patient_table.setItem(row_position, 0, QTableWidgetItem(str(patient.id)))
            self.patient_table.setItem(row_position, 1, QTableWidgetItem(patient.nom))
            self.patient_table.setItem(row_position, 2, QTableWidgetItem(str(patient.prenom)))
            
            # Age - avec tri numérique
            age_item = QTableWidgetItem()
            age_item.setData(Qt.DisplayRole, (datetime.datetime.now() - patient.date_naissance).days // 365)  # Utiliser setData pour tri numérique
            self.patient_table.setItem(row_position, 3, age_item)

            self.patient_table.setItem(row_position, 4, QTableWidgetItem(patient.niveau))
            self.patient_table.setItem(row_position, 5, QTableWidgetItem(patient.ecole))

            self.patient_table.setItem(row_position, 6, QTableWidgetItem(patient.date_naissance.strftime("%Y-%m-%d")))

            self.patient_table.setItem(row_position, 7, QTableWidgetItem(patient.ville))
            self.patient_table.setItem(row_position, 8, QTableWidgetItem(patient.telephone1))
            self.patient_table.setItem(row_position, 9, QTableWidgetItem(patient.email))
            self.patient_table.setItem(row_position,10,QTableWidgetItem(patient.etat_suivi))
        
        self.patient_table.setSortingEnabled(True)  # Réactiver le tri
    
    def display_patient_details(self, patient ):
        """Afficher les détails d'un patient dans le formulaire"""
        self.selected_patient_id = patient.id
        self.name_input.setText(patient.nom)
        self.prenom_input.setText(patient.prenom)
        self.age_input.setText(str((datetime.datetime.now() - patient.date_naissance).days // 365))
        self.sexe_input.setCurrentText(patient.sexe)
        self.date_naissance_input.setDate(patient.date_naissance)
        self.adresse_input.setText(patient.adresse)
        self.ville_input.setText(patient.ville)
        self.telephone1_input.setText(patient.telephone1)
        self.type_telephone1_input.setCurrentText(patient.typeTelephone1)
        self.telephone2_input.setText(patient.telephone2)
        self.type_telephone2_input.setCurrentText(patient.typeTelephone2)
        self.email_input.setText(patient.email)
        self.niveau_input.setCurrentText(patient.niveau)
        self.ecole_input.setText(patient.ecole)
        self.amenagement_input.setCurrentText(patient.amenagement)
        self.etat_suivi_input.setCurrentText(patient.etat_suivi)
        self.description_input.setText(patient.description)
    
    def get_patient_details(self):
        """Récupérer les valeurs du formulaire"""
        return Patient(
            id = self.selected_patient_id,
            nom=self.name_input.text(),
            prenom=self.prenom_input.text(),
            sexe=self.sexe_input.currentText(),
            date_naissance=datetime.datetime.strptime(self.date_naissance_input.date().toString("yyyy-MM-dd"), "%Y-%m-%d"),
            adresse=self.adresse_input.text(),
            ville=self.ville_input.text(),
            telephone1=self.telephone1_input.text(),
            telephone2=self.telephone2_input.text(),
            typeTelephone1=self.type_telephone1_input.currentText(),
            typeTelephone2=self.type_telephone2_input.currentText(),
            email=self.email_input.text(),
            niveau=self.niveau_input.currentText(),
            ecole=self.ecole_input.text(),
            amenagement=self.amenagement_input.currentText(),
            etat_suivi=self.etat_suivi_input.currentText(),
            description=self.description_input.toPlainText()
        )
    
    def get_selected_row(self):
        """Récupérer la ligne sélectionnée"""
        selected_items = self.patient_table.selectedItems()
        if selected_items:
            return selected_items[0].row()
        return None
    
    def update_table_row(self, row, patient):
        """Mettre à jour une ligne dans la table"""
        # ID - avec tri numérique
        id_item = QTableWidgetItem()
        id_item.setData(Qt.DisplayRole, patient.id)
        self.patient_table.setItem(row, 0, id_item)
        
        self.patient_table.setItem(row, 1, QTableWidgetItem(patient.nom))
        self.patient_table.setItem(row, 2, QTableWidgetItem(patient.prenom))
        
        # Age - avec tri numérique
        age_item = QTableWidgetItem()
        age_item.setData(Qt.DisplayRole, (datetime.datetime.now() - patient.date_naissance).days // 365)
        self.patient_table.setItem(row, 3, age_item)

        self.patient_table.setItem(row, 4, QTableWidgetItem(patient.niveau))
        self.patient_table.setItem(row, 5, QTableWidgetItem(patient.ecole))
        
        self.patient_table.setItem(row, 6, QTableWidgetItem(patient.date_naissance.strftime("%Y-%m-%d")))
        self.patient_table.setItem(row, 7, QTableWidgetItem(patient.ville))
        self.patient_table.setItem(row, 8, QTableWidgetItem(patient.telephone1))
        self.patient_table.setItem(row, 9, QTableWidgetItem(patient.email))
        self.patient_table.setItem(row,10,QTableWidgetItem(patient.etat_suivi))
    
    def filter_rows(self, search_text):
        """Filtrer les lignes selon le texte de recherche"""
        for row in range(self.patient_table.rowCount()):
            match = False
            for column in range(1,self.patient_table.columnCount()):
                item = self.patient_table.item(row, column)
                if item and search_text.lower() in item.text().lower():
                    match = True
                    break
            self.patient_table.setRowHidden(row, not match)
    
    def _on_validate_clicked(self):
        """Gérer le clic sur le bouton Valider"""
        updatedPatient = self.get_patient_details()
        self.patient_updated.emit(updatedPatient)
    
    def _on_creer_clicked(self):
        """Gérer le clic sur le bouton Créer un nouveau patient"""
        # Réinitialiser le formulaire
        patient = self.get_patient_details()
        self.patient_created.emit(patient)
        self.patient_table.clearSelection()
        self._on_clear_clicked()
    
    def _on_supprimer_clicked(self):
        """Gérer le clic sur le bouton Supprimer le patient"""
        selected_row = self.get_selected_row()
        if selected_row is not None:
            patient_id = int(self.patient_table.item(selected_row, 0).text())
            # Émettre un signal ou appeler une méthode du controller pour supprimer le patient
            self.patient_deleted.emit(patient_id)
            self.patient_table.clearSelection()
            self._on_clear_clicked()
    
    def _on_clear_clicked(self):
        """Gérer le clic sur le bouton Effacer les champs"""
        self.name_input.clear()
        self.prenom_input.clear()
        self.age_input.clear()
        self.sexe_input.setCurrentIndex(0)
        self.date_naissance_input.setDate(datetime.datetime.now())
        self.adresse_input.clear()
        self.ville_input.clear()
        self.telephone1_input.clear()
        self.type_telephone1_input.setCurrentIndex(0)
        self.telephone2_input.clear()
        self.type_telephone2_input.setCurrentIndex(0)
        self.email_input.clear()
        self.niveau_input.setCurrentIndex(0)
        self.ecole_input.clear()
        self.amenagement_input.setCurrentIndex(0)
        self.etat_suivi_input.setCurrentIndex(0)
        self.description_input.clear()

        self.patient_table.clearSelection()
        self.selected_patient_id = None