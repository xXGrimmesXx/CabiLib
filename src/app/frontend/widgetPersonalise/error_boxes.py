from PySide6.QtWidgets import QMessageBox
from PySide6.QtGui import QIcon

class BaseErrorBox(QMessageBox):
    """Classe de base poour les boîtes de dialogue d'erreur."""
    def __init__(self, parent=None, titre="Erreur", message="Une erreur est survenue.", details=None):
        super().__init__(parent)
        self.setWindowTitle(titre)
        self.setText(message)
        if details:
            self.setDetailedText(details)

class RegleMetierErrorBox(BaseErrorBox):
    def __init__(self, parent=None, message="Une règle métier n'a pas été respectée."):
        super().__init__(parent, titre="Attention - Règle métier", message=message)
        self.setIcon(QMessageBox.Warning)

class ConflitHoraireErrorBox(BaseErrorBox):
    def __init__(self, parent=None, message="Un conflit d'horaire a été détecté."):
        super().__init__(parent, titre="Conflit d'horaire", message=message)
        self.setIcon(QMessageBox.Warning)

class EntiteIntrouvableErrorBox(BaseErrorBox):
    def __init__(self, parent=None, message="L'élément demandé est introuvable."):
        super().__init__(parent, titre="Élément introuvable", message=message)
        self.setIcon(QMessageBox.Information)

class DatabaseErrorBox(BaseErrorBox):
    def __init__(self, parent=None, message="Une erreur de base de données est survenue."):
        super().__init__(parent, titre="Erreur Système (Base de données)", message=message)
        self.setIcon(QMessageBox.Critical)

class GoogleCalendarErrorBox(BaseErrorBox):
    def __init__(self, parent=None, message="Une erreur de synchronisation Google Calendar est survenue."):
        super().__init__(parent, titre="Erreur Google Calendar", message=message)
        self.setIcon(QMessageBox.Warning)

class ExceptionHandler:
    """Utilitaire pour afficher la bonne boîte de dialogue selon l'exception."""
    @staticmethod
    def handle(parent, exception):
        from app.exceptions import (
            RegleMetierException,
            ConflitHoraireException,
            EntiteIntrouvableException,
            DatabaseException,
            GoogleCalendarException
        )

        if isinstance(exception, ConflitHoraireException):
            box = ConflitHoraireErrorBox(parent, message=str(exception))
        elif isinstance(exception, RegleMetierException):
            box = RegleMetierErrorBox(parent, message=str(exception))
        elif isinstance(exception, EntiteIntrouvableException):
            box = EntiteIntrouvableErrorBox(parent, message=str(exception))
        elif isinstance(exception, DatabaseException):
            box = DatabaseErrorBox(parent, message=str(exception))
        elif isinstance(exception, GoogleCalendarException):
            box = GoogleCalendarErrorBox(parent, message=str(exception))
        else:
            box = BaseErrorBox(parent, titre="Erreur inconnue", message=str(exception))
            box.setIcon(QMessageBox.Critical)
        
        box.exec()
