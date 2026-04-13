from app.backend.services.ligneFacture_service import LigneFactureService
from app.backend.services.facture_service import FactureService
from app.frontend.widgetPersonalise.error_boxes import ExceptionHandler
from app.exceptions import CabiLibException

class SuivreFactureController:
    def __init__(self, model, view):
        self.view = view

        # Connecter les signaux de la vue aux méthodes du controller
        self.view.facture_selected.connect(self.on_facture_selected)
        #self.view.facture_updated.connect(self.on_facture_updated)
        self.view.search_changed.connect(self.on_search_changed)
        self.view.refresh.connect(self.on_refresh)
        self.load_factures()

    def on_refresh(self):
        # Logique à exécuter lors du refresh
        self.load_factures()

    def load_factures(self):
        try:
            # FactureService instancié
            service = FactureService()
            factures_objects = service.get_all_factures()
            self.view.load_factures(factures_objects)
        except CabiLibException as e:
            ExceptionHandler.handle(self.view, e)

    def on_search_changed(self, search_text):
        self.view.filter_rows(search_text)
    
    def on_facture_selected(self, row):
        try:
            facture_id = self.view.facture_table.item(row, 0).text()
            service = FactureService()
            facture = service.get_facture_by_id(facture_id)
        
            lignes_facture = LigneFactureService.get_lignes_by_facture_id(facture_id)
        
            self.view.display_facture_details(facture, lignes_facture)
        except CabiLibException as e:
            ExceptionHandler.handle(self.view, e)