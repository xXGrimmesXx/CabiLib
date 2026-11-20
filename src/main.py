from app.backend.database.update_schema import ensure_db
import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QPalette, QColor, QIcon
from app.frontend.views.main_window_view import MainWindow
from app.frontend.controllers.main_controller import MainController
import app.backend.services.internet_API_thread_worker as api_worker
import app.backend.services.constantes_manager as cm
import app.backend.database.database as db
import time


import argparse

def main():
    """Point d'entrée de l'application"""
    # 1. Configuration de l'analyseur d'arguments
    entrypoint = time.time()
    parser = argparse.ArgumentParser(description="Lancement de CabiLib")
    parser.add_argument('--beta', type=str, metavar='CHEMIN_CODE', help="Activer le mode beta et spécifier le chemin du code de l'application")
    
    # 2. Récupérations des arguments (ignorer les arguments spécifiques à Qt/PySide)
    args, unknown = parser.parse_known_args()

    # 3. Utilisation des arguments
    if args.beta:
        import os
        cm.CONST_PATH = os.path.join(args.beta, "Constantes.json")
        db.update_db_path(os.path.join(args.beta, "app", "backend", "database", "CabiLib.db"))
    print(db.DB_PATH)
    init_db = time.time()
    ensure_db()
    db_ready = time.time()
    
    app = QApplication(sys.argv)

    app_created = time.time()

    
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

    colors_ready = time.time()

    
    
    # Créer la fenêtre principale
    main_window = MainWindow()
    controller = MainController(main_window)

    window_ready = time.time()

    main_window.show()
    window_ready = time.time()

    
    api_worker.start_api_worker(60,60)
    api_ready = time.time()

    print(f"""Temps d'initialisation :
        Entrypoint -> Init DB: {init_db - entrypoint:.2f}s,
        Init DB -> DB Ready: {db_ready - init_db:.2f}s,
        DB Ready -> App Created: {app_created - db_ready:.2f}s,
        App Created -> Window Ready: {window_ready - app_created:.2f}s,
        Window Ready -> Colors Ready: {colors_ready - window_ready:.2f}s,
        Colors Ready -> API Ready: {api_ready - colors_ready:.2f}s
          """)

    # Lancer l'application
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
