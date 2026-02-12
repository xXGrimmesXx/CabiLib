from PySide6.QtWidgets import (QWidget, QHBoxLayout, QDateEdit, QLabel, QPushButton, QVBoxLayout, QMessageBox)
from PySide6.QtCore import Qt, Signal

from datetime import datetime, timedelta


class CabinetView(QWidget):
    """VIEW - Interface graphique pour la gestion des patients"""
    
    # Signaux pour communiquer avec le Controller
    generation_redevance: Signal = Signal(datetime, datetime)
    """Signal émis pour générer la redevance entre deux dates."""
    
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
        main_layout = QVBoxLayout()
        

        titre_redevance = QLabel("Génération de la Redevance")
        titre_redevance.setStyleSheet("font-size: 18pt; font-weight: bold;")
        titre_redevance.setAlignment(Qt.AlignCenter)
        titre_redevance.setContentsMargins(0, 20, 0, 20)
        main_layout.addWidget(titre_redevance)

         # Sélecteur de date
        date_layout = QHBoxLayout()
        date_layout.addWidget(QLabel("Date de début :"))
        start_date = datetime(datetime.now().year, datetime.now().month, 1)
        self.start_date_edit = QDateEdit(start_date)
        self.start_date_edit.setCalendarPopup(True)
        date_layout.addWidget(self.start_date_edit)

        date_layout.addWidget(QLabel("Date de fin :"))
        # dernier jour du mois courant
        if start_date.month == 12:
            end_date = datetime(start_date.year+1, 1, 1)-timedelta(days=1)
        else:
            end_date = datetime(start_date.year, start_date.month+1, 1)-timedelta(days=1)
        self.end_date_edit = QDateEdit(end_date)
        self.end_date_edit.setCalendarPopup(True)

        date_layout.addWidget(self.end_date_edit)
        date_layout.addStretch()
        date_layout.setContentsMargins(0, 20, 0, 20)

        main_layout.addLayout(date_layout)

        # Bouton de génération
        self.generate_button = QPushButton("Générer la Redevance")
        self.generate_button.clicked.connect(self.on_generate_clicked)
        main_layout.addWidget(self.generate_button)

        main_layout.addStretch()

        self.setLayout(main_layout)

    def on_generate_clicked(self) -> None:
        start_date = self.start_date_edit.date().toPython()
        start_date = datetime(start_date.year, start_date.month, start_date.day, 0, 0, 0)
        end_date = self.end_date_edit.date().toPython()
        end_date = datetime(end_date.year, end_date.month, end_date.day, 23, 59, 59,999999)
        
        self.generation_redevance.emit(start_date, end_date)

    def show_error_message(self, message) -> None:
        """ Affiche un message d'erreur à l'utilisateur. 
        Args: 
            message (str): Le message d'erreur à afficher. 
        """
        QMessageBox.critical(self, "Erreur", message)
