from datetime import date

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel,
                               QHBoxLayout, QVBoxLayout, QDateEdit,
                               QTableWidget, QPushButton,
                               QTableWidgetItem, QLineEdit)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QIntValidator, QBrush
from app.backend.model.typeRDV import TypeRDV
from app.frontend.widgetPersonalise.checkable_combobox import CheckableComboBox
from app.frontend.widgetPersonalise.separator import Separator
from app.frontend.widgetPersonalise.error_boxes import ExceptionHandler
import app.exceptions

class CreerDevisView(QWidget):
    """VIEW - Interface graphique pour la gestion des devis"""

    devis_generer: Signal = Signal(int, object, object, object)
    """Signal émis pour générer le devis (id patient, date de début, date de fin, dictionnaire des actes avec quantités)."""
    devis_preview: Signal = Signal(int, object, object, object)
    """Signal émis pour prévisualiser le devis (id patient, date de début, date de fin, dictionnaire des actes avec quantités)."""
    refresh_sig: Signal = Signal()
    """Signal émis pour rafraîchir la vue avec les dernières données."""

    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.qtt_actes_input = []

    def setup_ui(self):
        """
        Crée et configure l'interface utilisateur pour la création de devis.
        """
        layout = QVBoxLayout(self)
        label = QLabel("Création de devis")
        label.setStyleSheet("font-size: 18px; font-weight: bold;")
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)

        layout.addWidget(Separator())

        patient_box = QHBoxLayout()
        patient_label = QLabel("Patient :")
        patient_label.setStyleSheet("font-weight: bold;")
        patient_box.addWidget(patient_label)
        self.patient_combobox = CheckableComboBox(unique=True)
        patient_box.addWidget(self.patient_combobox)
        patient_box.addStretch()
        layout.addLayout(patient_box)

        date_box = QHBoxLayout()
        titre_date = QLabel("Période du devis : ")
        titre_date.setStyleSheet("font-weight: bold;")
        date_box.addWidget(titre_date)
        date_box.addWidget(QLabel("du "))
        self.date_debut = QDateEdit()
        self.date_debut.setCalendarPopup(True)
        date_box.addWidget(self.date_debut)
        date_box.addWidget(QLabel(" au "))
        self.date_fin = QDateEdit()
        self.date_fin.setCalendarPopup(True)
        date_box.addWidget(self.date_fin)
        date_box.addStretch()

        layout.addLayout(date_box)
        layout.addWidget(Separator())

        self.actes_table = QTableWidget(0, 2)
        self.actes_table.setHorizontalHeaderLabels(["Acte", "Quantité"])

        layout.addWidget(self.actes_table)

        buttonLayout = QHBoxLayout()
        buttonLayout.addStretch()
        layout.addLayout(buttonLayout)
        self.preview_button = QPushButton("Prévisualiser le devis")
        self.preview_button.clicked.connect(self.preview_devis)
        buttonLayout.addWidget(self.preview_button)
        buttonLayout.addStretch()
        self.generate_button = QPushButton("Générer le devis")
        self.generate_button.clicked.connect(self.generate_devis)
        buttonLayout.addWidget(self.generate_button)
        buttonLayout.addStretch()






    def set_patient_list(self, patients):
        """Met à jour la liste des patients dans le combo box.
        args:
            patients (list): Liste des objets Patient à afficher.
        """
        print("CreerDevisView: Updating patient list in combo box...")
        self.patient_combobox.clear()
        for patient in patients:
            display_text = f"{patient.nom} {patient.prenom}"
            self.patient_combobox.addItem(display_text, patient.id)

    def add_acte_row(self, type_rdv : TypeRDV):
        """Ajoute une ligne à la table des actes.
        args:
            type_rdv (TypeRDV): L'objet TypeRDV représentant l'acte à afficher.
        """
        row_count = self.actes_table.rowCount()
        self.actes_table.insertRow(row_count)
        item_acte = QTableWidgetItem(type_rdv.nom)
        item_acte.setBackground(QBrush(QColor(type_rdv.couleur)))
        item_acte.setData(Qt.UserRole, type_rdv.id)  # Stocker l'id de l'acte dans l'item
        self.actes_table.setItem(row_count, 0, item_acte)
        self.qtt_actes_input.append(QLineEdit())
        self.qtt_actes_input[-1].setValidator(QIntValidator())
        self.qtt_actes_input[-1].setProperty("acte_id", type_rdv.id)  # Stocker l'id de l'acte dans le QLineEdit
        self.qtt_actes_input[-1].setText("0")
        self.qtt_actes_input[-1].setStyleSheet(f"background-color: {type_rdv.couleur};")

        self.actes_table.setCellWidget(row_count, 1, self.qtt_actes_input[-1])
        self.actes_table.resizeColumnsToContents()
        self.actes_table.resizeRowsToContents()

    def refresh_actes(self, type_rdvs : list[TypeRDV]):
        """Rafraîchit la table des actes avec une nouvelle liste d'actes.
        args:
            actes (list): Liste de tuples (id_acte, libelle_acte) à afficher.
        """
        print("CreerDevisView: Refreshing actes table with new data...")
        type_present = [i.property("acte_id") for i in self.qtt_actes_input]
        for t in type_rdvs:
            if t.id not in type_present:
                self.add_acte_row(t)

    def on_refresh(self):
        """Méthode à appeler pour rafraîchir les données de la vue."""
        print("CreerDevisView: on_refresh called, emitting refresh_view signal...")
        self.refresh_sig.emit()
    
    def get_selected_patient_id(self) -> int | None:
        """Retourne l'identifiant du patient sélectionné dans le combo box.
        Returns:
            int | None: L'identifiant du patient sélectionné, ou None si aucun patient n'est sélectionné.
        """
        data = self.patient_combobox.selectedData()
        return data[0] if len(data) > 0 else None
    
    def get_actes_qtt(self) -> dict[int, float]:
        """Retourne la liste des actes et de leurs quantités sélectionnées.
        Returns:
            dict[int, float]: Dictionnaire avec les identifiants des type RDV comme clés et leurs quantités comme valeurs.
        """
        actes_qtt = {}
        for i in range(self.actes_table.rowCount()):
            item = self.actes_table.item(i, 0)
            if item is not None:
                acte_id = item.data(Qt.UserRole)
                qtt_str = self.actes_table.cellWidget(i, 1).text()
                if qtt_str:
                    try:
                        qtt = float(qtt_str)
                        if qtt < 0:
                            import app.exceptions
                            raise app.exceptions.RegleMetierException(f"La quantité pour l'acte '{item.text()}' ne peut pas être négative.")
                        elif qtt > 0:
                            actes_qtt[acte_id] = qtt
                    except ValueError as e:
                        raise app.exceptions.RegleMetierException(f"Quantité invalide pour l'acte '{item.text()}'. Veuillez entrer un nombre valide.") from e
        return actes_qtt
    
    def get_date_debut(self) -> date:
        """Retourne la date de début sélectionnée.
        Returns:
            datetime.date: La date de début sélectionnée.
        """
        return self.date_debut.date().toPython()
    
    def get_date_fin(self) -> date:
        """Retourne la date de fin sélectionnée.
        Returns:
            datetime.date: La date de fin sélectionnée.
        """
        return self.date_fin.date().toPython()
    

    def preview_devis(self):
        """Génère une prévisualisation du devis en fonction des données saisies."""
        try:
            id_patient = self.get_selected_patient_id()
            if id_patient is None:
                raise app.exceptions.RegleMetierException("Veuillez sélectionner un patient pour prévisualiser le devis.")
            date_debut = self.get_date_debut()
            date_fin = self.get_date_fin()

            if date_debut > date_fin:
                raise app.exceptions.RegleMetierException("La date de début doit être antérieure à la date de fin pour prévisualiser le devis.")
            actes_qtt = self.get_actes_qtt()

            self.devis_preview.emit(id_patient, date_debut, date_fin, actes_qtt)
        except Exception as e:
            ExceptionHandler.handle(self, e)

    def generate_devis(self):
        """Génère le devis final en fonction des données saisies."""
        try:
            id_patient = self.get_selected_patient_id()
            if id_patient is None:
                raise app.exceptions.RegleMetierException("Veuillez sélectionner un patient pour générer le devis.")
            date_debut = self.get_date_debut()
            date_fin = self.get_date_fin()

            if date_debut > date_fin:
                raise app.exceptions.RegleMetierException("La date de début doit être antérieure à la date de fin pour générer le devis.")
            actes_qtt = self.get_actes_qtt()

            self.devis_generer.emit(id_patient, date_debut, date_fin, actes_qtt)
        except Exception as e:
            ExceptionHandler.handle(self, e)