import sqlite3
from app.database.setup_db import initDB
import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QPalette, QColor, QIcon
from app.views.main_window_view import MainWindow
from app.controllers.main_controller import MainController

import app.services.calendar_api as calendar_api

def main():
    """Point d'entrée de l'application"""
    #initDB()
    # Initialiser les données de test
    #initAllTestData()
    try : 
        calendar_api.create_calendar_if_not_exist()
    except Exception as e:
        print(f"[ERREUR] {e}")
    
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


if __name__ == '__main__':
    main()
