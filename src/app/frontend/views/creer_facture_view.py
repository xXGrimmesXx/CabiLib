from PySide6.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QDateEdit,
                               QRadioButton, QButtonGroup, QLabel, QComboBox,
                               QCompleter, QPushButton, QMessageBox)
from PySide6.QtCore import Qt, Signal
from app.backend.model.facture import Facture
from app.backend.model.patient import Patient
from app.backend.model.rendezVous import RendezVous
from app.frontend.widgetPersonalise.separator import Separator
from app.frontend.widgetPersonalise.checkable_combobox import CheckableComboBox
from datetime import datetime


class creerFactureView(QWidget):
    """VIEW - Interface graphique pour la gestion des patients"""
    
    # Signaux pour communiquer avec le Controller
    facture_generer: Signal = Signal(object, object, list)
    """Signal émis pour générer la facture pour les patient selectionnés (date de début, date de fin, ids patients)."""
    facture_preview: Signal = Signal(object, object, list)
    """Signal émis pour prévisualiser la facture pour les patients selectionnés (date de début, date de fin, ids patients)."""
    date_changed: Signal = Signal(object,object)
    """Signal émis lorsque les dates de début ou de fin sont modifiées (date debut, date de fin)."""
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
        facture_option.addWidget(QLabel("Selectionner les patients à facturer : "))
        self.patient_factures = CheckableComboBox()
        facture_option.addWidget(self.patient_factures)
        facture_option.addStretch()

        facture_option.setContentsMargins(0, 20, 0, 20)
        
        self.main_layout.addLayout(facture_option)
        self.main_layout.addWidget(Separator(Qt.Horizontal))

        # Sélecteur de date
        date_layout = QHBoxLayout()
        date_layout.addWidget(QLabel("Date de début :"))
        self.start_date_edit = QDateEdit(datetime.now())
        self.start_date_edit.setCalendarPopup(True)
        self.start_date_edit.dateChanged.connect(lambda: self.date_changed.emit(self.start_date_edit.date().toPython(), self.end_date_edit.date().toPython()))
        date_layout.addWidget(self.start_date_edit)

        date_layout.addWidget(QLabel("Date de fin :"))
        self.end_date_edit = QDateEdit(datetime.now())
        self.end_date_edit.setCalendarPopup(True)
        self.end_date_edit.dateChanged.connect(lambda: self.date_changed.emit(self.start_date_edit.date().toPython(), self.end_date_edit.date().toPython()))
        date_layout.addWidget(self.end_date_edit)
        date_layout.addStretch()
        date_layout.setContentsMargins(0, 20, 0, 20)

        self.main_layout.addLayout(date_layout)

        self.main_layout.addWidget(Separator(Qt.Horizontal))

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

    def set_patient_list(self, patients : list[Patient]):
        """Remplir la liste des patients"""
        self.patient_factures.clear()
        for patient in patients:
            self.patient_factures.addItem(f"{patient.prenom} {patient.nom}", patient.id)

    def on_creer_clicked(self) :
        start_date = self.start_date_edit.date().toPython()
        start_date = datetime(start_date.year, start_date.month, start_date.day)

        end_date = self.end_date_edit.date().toPython()
        end_date = datetime(end_date.year, end_date.month, end_date.day,23,59,59,999999)

        self.facture_generer.emit(start_date,end_date,self.patient_factures.selectedData())

    def on_preview_clicked(self) :
        start_date = self.start_date_edit.date().toPython()
        start_date = datetime(start_date.year, start_date.month, start_date.day)

        end_date = self.end_date_edit.date().toPython()
        end_date = datetime(end_date.year, end_date.month, end_date.day,23,59,59,999999)

        
        self.facture_preview.emit(start_date,end_date,self.patient_factures.selectedData())


    def erreur_completion_rdv(self, patient: Patient, rdvs_a_renseigner: list[RendezVous]):
        """Afficher une erreur si des rendez-vous n'ont pas de statut de présence défini"""
        msg = f"Le patient {patient.prenom} {patient.nom} a des rendez-vous sans statut de présence défini :\n"
        for rdv in rdvs_a_renseigner:
            msg += f"- Rendez-vous du {rdv.date.strftime('%d/%m/%Y à %H:%M')}\n"
        msg += "Veuillez renseigner le statut de présence avant de facturer."
        
        QMessageBox.warning(self, "Erreur de facturation", msg)

    def erreur_patient_absent(self, patient: Patient, rdvs_patient_absent: list[RendezVous], absence_precedentes: list[RendezVous]):
        """Afficher une alerte si le patient a des absences"""
        msg = f"Le patient {patient.prenom} {patient.nom} a des absences aux rendez-vous suivants :\n"
        for rdv in rdvs_patient_absent:
            msg += f"- Rendez-vous du {rdv.date.strftime('%d/%m/%Y à %H:%M')}\n"
            
        #print("Absence précédentes du patient :\n",absence_precedentes)
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

    def erreur_generation_facture(self,patient:Patient):
        """Afficher une erreur de génération de facture"""
        msg = f"Aucune facture n'a pu être générée pour {patient.prenom} {patient.nom}."
        QMessageBox.warning(self, "Erreur de génération de facture", msg)