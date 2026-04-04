from datetime import datetime
import webbrowser

import app.backend.services.redevance_generator as rg
from app.frontend.views.redevance_view import RedevanceView


class RedevanceController:
    def __init__(self, view: RedevanceView):
        self.view = view
        self._connect_signals()

    def _connect_signals(self) -> None:
        """Connecte les signaux de la vue aux méthodes du contrôleur."""
        self.view.generation_redevance.connect(self.on_generation_redevance)

    def on_generation_redevance(self, start_date: datetime, end_date: datetime) -> None:
        """Gère la génération de la redevance pour une période donnée."""
        try:
            pdf_path = rg.create_and_save_pdf(start_date, end_date)
            webbrowser.open(pdf_path)
        except Exception as e:
            self.view.show_error_message(str(e))
