import sqlite3
import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QPalette, QColor, QIcon
from PySide6.QtCore import Qt
from app.views.main_window_view import MainWindow
from app.controllers.main_controller import MainController

from app.model.facture import Facture
from app.model.patient import Patient
from app.model.ligneFacture import LigneFacture

from app.database.setup_db import initDB,DB_PATH
from app.database.testData import initAllTestData

from app.utils.facture_generator import generate_facture_pdf,save_facture_pdf
from app.utils import constantes_manager

import os

def main():
    """Point d'entrée de l'application"""
    #nitDB()
    # Initialiser les données de test
    #initAllTestData()
    with open(os.path.join(os.environ['APPDATA'], 'CabiLib', "error_log.txt"), "a") as log_file:
            log_file.write(f"[DEBUG] Chemin de la BDD : {DB_PATH}\n")
            log_file.close()
    try :

        connexion = sqlite3.connect(DB_PATH)
        cursor = connexion.cursor()
        cursor.execute("DELETE from ligne_facture")
        cursor.execute("DELETE from facture")
        cursor.execute("UPDATE rendez_vous SET facture_id = NULL")
        connexion.commit()
        connexion.close()    
        
        app = QApplication(sys.argv)
        app.setApplicationName("CabiLib - Gestion Cabinet")

        app.setWindowIcon(QIcon('cabilib_logo.png'))      
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

    except Exception as e:
        print(f"Erreur lors du lancement de l'application : {e}")
        with open(os.path.join(os.environ['APPDATA'], 'CabiLib', "error_log.txt"), "a") as log_file:
            log_file.write(f"Erreur lors du lancement de l'application : {e}\n")
        log_file.close()


if __name__ == '__main__':
    main()
