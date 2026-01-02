from PySide6.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QDateEdit,
                               QRadioButton, QButtonGroup, QLabel, QComboBox,
                               QCompleter, QPushButton, QMessageBox)
from PySide6.QtCore import Qt, Signal
from app.model.facture import Facture
from app.widgetPersonalise.separator import Separator
from datetime import datetime


class creerFactureView(QWidget):
    """VIEW - Interface graphique pour la gestion des patients"""
    
    # Signaux pour communiquer avec le Controller
    generate_facture_clicked: Signal = Signal(object)
    """Signal émis lors du clic pour générer une facture (options de facturation)."""
    mass_facture_generer: Signal = Signal(object, object)
    """Signal émis pour générer des factures en masse (date de début, date de fin)."""
    single_facture_generer: Signal = Signal(object, object, int)
    """Signal émis pour générer une facture individuelle (date de début, date de fin, id patient)."""
    mass_facture_preview: Signal = Signal(object, object)
    """Signal émis pour prévisualiser des factures en masse (date de début, date de fin)."""
    single_facture_preview: Signal = Signal(object, object, int)
    """Signal émis pour prévisualiser une facture individuelle (date de début, date de fin, id patient)."""
    refresh: Signal = Signal()
    """Signal pour rafraîchir la vue de facturation."""
    
    def __init__(self) -> None:
        """
        Initialise la vue de création de factures.
        """
        super().__init__()
        self.setup_ui()
    
    def setup_ui(self) -> None:
        """
        Crée et configure l'interface utilisateur pour la création de factures.
        """
        """Création de l'interface utilisateur"""

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setAlignment(Qt.AlignTop)
        titre = QLabel("Facturer les patients")
        titre.setContentsMargins(0, 0, 0, 20)
        titre.setAlignment(Qt.AlignCenter)
        titre.setStyleSheet("font-size: 18pt; font-weight: bold;")
        self.main_layout.addWidget(titre)

        self.main_layout.addWidget(Separator(Qt.Horizontal))

        facture_option = QHBoxLayout()
        facture_option.setSizeConstraint(QHBoxLayout.SetMinimumSize)
        facture_option.addWidget(QLabel("Options de facturation :"))
        self.mass_facture_button = QRadioButton("Facturer tous les patients")
        self.single_facture_button = QRadioButton("Facturer un seul patient")

        self.mass_facture_button.clicked.connect(self.on_mass_facture_clicked)
        self.single_facture_button.clicked.connect(self.on_single_facture_clicked)

        self.button_group = QButtonGroup()
        self.button_group.addButton(self.mass_facture_button)
        self.button_group.addButton(self.single_facture_button)
        self.mass_facture_button.setChecked(True)

        facture_option.addWidget(self.mass_facture_button)
        facture_option.addWidget(self.single_facture_button)
        facture_option.addStretch()

        facture_option.setContentsMargins(0, 20, 0, 20)
        
        self.main_layout.addLayout(facture_option)
        self.main_layout.addWidget(Separator(Qt.Horizontal))

        # Sélecteur de date
        date_layout = QHBoxLayout()
        date_layout.addWidget(QLabel("Date de début :"))
        self.start_date_edit = QDateEdit(datetime.now())
        self.start_date_edit.setCalendarPopup(True)
        date_layout.addWidget(self.start_date_edit)

        date_layout.addWidget(QLabel("Date de fin :"))
        self.end_date_edit = QDateEdit(datetime.now())
        self.end_date_edit.setCalendarPopup(True)

        date_layout.addWidget(self.end_date_edit)
        date_layout.addStretch()
        date_layout.setContentsMargins(0, 20, 0, 20)

        self.main_layout.addLayout(date_layout)

        self.main_layout.addWidget(Separator(Qt.Horizontal))

        #option pour la facturation individuelle

        self.factu_individuelle_widget = QWidget()
        self.factu_individuelle_widget.setHidden(True)
        self.main_layout.addWidget(self.factu_individuelle_widget)

        patient_section_layout = QVBoxLayout(self.factu_individuelle_widget)
        patient_layout = QHBoxLayout()
        patient_section_layout.addLayout(patient_layout)
        patient_layout.addWidget(QLabel("Selectionner le patient"))

        self.patient_input = QComboBox()
        self.patient_input.setEditable(True)
        self.patient_completer = QCompleter()
        self.patient_completer.setCaseSensitivity(Qt.CaseInsensitive)  # Insensible à la casse
        self.patient_completer.setFilterMode(Qt.MatchContains)  # Filtre par contenu (pas seulement début)
        self.patient_input.setCompleter(self.patient_completer)
        patient_layout.addWidget(self.patient_input)

        patient_layout.addStretch()

        patient_section_layout.addWidget(Separator(Qt.Horizontal))
        patient_section_layout.setContentsMargins(0, 20, 0, 20)

        generation_layout = QHBoxLayout()
        self.main_layout.addLayout(generation_layout)
        
        self.preview_button = QPushButton("Aperçu avant impression")
        self.preview_button.clicked.connect(self.on_preview_clicked)
        generation_layout.addWidget(self.preview_button)

        self.creer_button = QPushButton("Générer les factures")
        self.creer_button.clicked.connect(self.on_creer_clicked)
        generation_layout.addWidget(self.creer_button)

        

    def on_refresh(self):
        self.refresh.emit()

    def set_patient_list(self, patients):
        """Remplir la liste des patients"""
        self.patient_input.clear()
        self.patient_input.addItem("",-1)
        for patient in patients:
            self.patient_input.addItem(f"{patient.prenom} {patient.nom}", patient.id)
        # Utiliser le modèle du QComboBox pour le QCompleter
        self.patient_completer.setModel(self.patient_input.model())
        self.patient_completer.setCompletionRole(Qt.DisplayRole)
        self.patient_completer.activated.connect(self.patient_input.setCurrentIndex)

    def on_mass_facture_clicked(self) :
        self.factu_individuelle_widget.setHidden(True)
        self.creer_button.setText("Générer les factures")

    def on_single_facture_clicked(self) :
        self.factu_individuelle_widget.setHidden(False)
        self.creer_button.setText("Générer la facture")

    def on_creer_clicked(self) :
        start_date = self.start_date_edit.date().toPython()
        start_date = datetime(start_date.year, start_date.month, start_date.day)

        end_date = self.end_date_edit.date().toPython()
        end_date = datetime(end_date.year, end_date.month, end_date.day,23,59,59,999999)

        if(self.mass_facture_button.isChecked()) :
            print("Emission du signal de facturation de masse")
            self.mass_facture_generer.emit(start_date,end_date)
        else :
            patient_id = self.patient_input.currentData()
            print("Emission du signal de facturation individuelle pour le patient ID :",patient_id)
            self.single_facture_generer.emit(start_date,end_date,patient_id)

    def on_preview_clicked(self) :
        start_date = self.start_date_edit.date().toPython()
        start_date = datetime(start_date.year, start_date.month, start_date.day)

        end_date = self.end_date_edit.date().toPython()
        end_date = datetime(end_date.year, end_date.month, end_date.day,23,59,59,999999)

        if(self.mass_facture_button.isChecked()) :
            print("Emission du signal de preview de masse")
            self.mass_facture_preview.emit(start_date,end_date)
        else :
            patient_id = self.patient_input.currentData()
            print("Emission du signal de preview individuelle pour le patient ID :",patient_id)
            self.single_facture_preview.emit(start_date,end_date,patient_id)


    def erreur_completion_rdv(self, patient, rdvs_a_renseigner):
        """Afficher une erreur si des rendez-vous n'ont pas de statut de présence défini"""
        msg = f"Le patient {patient.prenom} {patient.nom} a des rendez-vous sans statut de présence défini :\n"
        for rdv in rdvs_a_renseigner:
            msg += f"- Rendez-vous du {rdv.date.strftime('%d/%m/%Y à %H:%M')}\n"
        msg += "Veuillez renseigner le statut de présence avant de facturer."
        
        QMessageBox.warning(self, "Erreur de facturation", msg)

    def erreur_patient_absent(self, patient, rdvs_patient_absent,absence_precedentes):
        """Afficher une alerte si le patient a des absences"""
        msg = f"Le patient {patient.prenom} {patient.nom} a des absences aux rendez-vous suivants :\n"
        for rdv in rdvs_patient_absent:
            msg += f"- Rendez-vous du {rdv.date.strftime('%d/%m/%Y à %H:%M')}\n"
            
        print("Absence précédentes du patient :\n",absence_precedentes)
        if(len(absence_precedentes)>0) :
            msg += "\nHistorique des absences précédentes :\n"
            for rdv in absence_precedentes:
                if(rdv is not None) :
                    msg += f"- Rendez-vous du {rdv.date.strftime('%d/%m/%Y à %H:%M')} : {rdv.presence}\n"

        msg += "\nVoulez-vous tout de même facturer les absences ?"
        
        reply = QMessageBox.question(self, "Absences détectées", msg, QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        return reply == QMessageBox.Yes
    
    def confirmation_facture_generee(self,facture: list[Facture]):
        """Afficher une confirmation de génération de facture"""
        msg = "Facture(s) générée(s) avec succès :\n"
        for fac in facture:
            msg += f"- Facture N° {fac.id} pour le patient ID {fac.patient_id}\n"
        
        QMessageBox.information(self, "Facture générée", msg)

    def erreur_generation_facture(self):
        """Afficher une erreur de génération de facture"""
        msg = "Aucune facture n'a pu être générée pour le patient sélectionné."
        QMessageBox.warning(self, "Erreur de génération de facture", msg)