
from datetime import datetime
import app.services.redevance_generator as rg
import webbrowser

from app.views.cabinet_view import CabinetView


class CabinetController:
    def __init__(self, view: CabinetView):
        """
        Initialise le contrôleur pour la vue de création de factures.
        Args:
            view (CabinetView): Instance de la vue CabinetView.
        """
        self.view = view
        self._connect_signals()
        # Connecter les signaux de la vue aux méthodes du contrôleur
    def _connect_signals(self) -> None:
        """
        Connecte les signaux de la vue aux méthodes du contrôleur.
        """
        self.view.generation_redevance.connect(self.on_generation_redevance)


    def on_generation_redevance(self, start_date: datetime, end_date: datetime) -> None:
        """
        Gère la génération de la redevance pour une période donnée.
        Args:
            start_date (datetime): Date de début de la période de facturation.
            end_date (datetime): Date de fin de la période de facturation.
        """
        print(f"Generation de la redevance entre {start_date} et {end_date}")
        # Appeler la fonction de génération de la redevance
        try :
            pdf_path = rg.create_and_save_pdf(start_date, end_date)# Ouvrir le PDF généré
            webbrowser.open(pdf_path)
        except Exception as e: 
            self.view.show_error_message(str(e))



