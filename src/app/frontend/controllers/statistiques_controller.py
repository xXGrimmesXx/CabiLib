from app.frontend.views.statistiques_view import StatistiquesView

from app.backend.model.rendezVous import RendezVous

from datetime import datetime


class StatistiquesController:
    def __init__(self, view: StatistiquesView):
        self.view = view

        montant_mois = RendezVous.get_montant_mois(datetime.now())
        montant_année = RendezVous.get_montant_année_courante(datetime.now())

        mois, CA = RendezVous.get_historique_chiffre_affaire_plusmoins_6_mois(datetime.now())
        self.view.update_graph(mois, CA)  # Mettre à jour le graph avec les données

        self.view.update_montants(montant_mois, montant_année)  # Mettre à jour les montants affichés

    def refresh (self):
        """Rafraîchit les données affichées dans la vue."""
        montant_mois = RendezVous.get_montant_mois(datetime.now())
        montant_année = RendezVous.get_montant_année_courante(datetime.now())
        mois, CA = RendezVous.get_historique_chiffre_affaire_plusmoins_6_mois(datetime.now())
        self.view.update_graph(mois, CA)  # Mettre à jour le graph avec les données
        self.view.update_montants(montant_mois, montant_année)  # Mettre à jour les montants affichés

        