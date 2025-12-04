import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QPalette, QColor
from PySide6.QtCore import Qt
from app.views.main_window_view import MainWindow
from app.controllers.main_controller import MainController

from app.model.facture import Facture
from app.model.patient import Patient
from app.model.ligneFacture import LigneFacture

from database.setup_db import initDB
from database.testData import initAllTestData

from utils.facture_generator import generate_facture_pdf,save_facture_pdf
from utils import constantes_manager


def main():
    """Point d'entrée de l'application"""
    #initDB()
    # Initialiser les données de test
    #initAllTestData()
    
    """
    #test de generation de facture pdf avec des vrai données
    facture = Facture.getAllFactures()[0]
    patient = Patient.getPatientById(facture.patient_id)
    lignes = LigneFacture.getAllLignesByFactureId(facture.id)
    pdf_bytes = generate_facture_pdf(facture, patient, lignes)
    save_facture_pdf(pdf_bytes, constantes_manager.get_constante("FACTURES_DIR"), f"{facture.id}.pdf")
    """
    
    
    app = QApplication(sys.argv)
    app.setApplicationName("CabiLib - Gestion Cabinet")
      
    # Forcer le mode clair avec palette personnalisée
    app.setStyle("Fusion")
    
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(255, 255, 255))  # Fond blanc
    palette.setColor(QPalette.WindowText, QColor(0, 0, 0))  # Texte noir
    palette.setColor(QPalette.Base, QColor(255, 255, 255))  # Fond des widgets blanc
    palette.setColor(QPalette.AlternateBase, QColor(245, 245, 245))  # Lignes alternées gris très clair
    palette.setColor(QPalette.ToolTipBase, QColor(255, 255, 220))  # Fond tooltip jaune clair
    palette.setColor(QPalette.ToolTipText, QColor(0, 0, 0))  # Texte tooltip noir
    palette.setColor(QPalette.Text, QColor(0, 0, 0))  # Texte noir
    palette.setColor(QPalette.Button, QColor(240, 240, 240))  # Boutons gris clair
    palette.setColor(QPalette.ButtonText, QColor(0, 0, 0))  # Texte boutons noir
    palette.setColor(QPalette.BrightText, QColor(255, 0, 0))  # Texte en surbrillance rouge
    palette.setColor(QPalette.Link, QColor(0, 0, 255))  # Liens bleus
    palette.setColor(QPalette.Highlight, QColor(0, 120, 215))  # Sélection bleu Windows
    palette.setColor(QPalette.HighlightedText, QColor(255, 255, 255))  # Texte sélectionné blanc
    
    app.setPalette(palette)
    
    # Créer la fenêtre principale
    main_window = MainWindow()
    controller = MainController(main_window)

    main_window.show()

    # Lancer l'application
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
