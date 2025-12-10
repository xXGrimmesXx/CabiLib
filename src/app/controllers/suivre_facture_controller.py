from app.model.facture import Facture
from app.model.ligneFacture import LigneFacture

class SuivreFactureController:
    def __init__(self, model, view):
        self.facturemodel = model
        self.ligneFactureModel = LigneFacture
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
        factures_objects = self.facturemodel.getAllFactures()
        self.view.load_factures(factures_objects)

    def on_search_changed(self, search_text):
        self.view.filter_rows(search_text)
    
    def on_facture_selected(self, row):
        facture_id = self.view.facture_table.item(row, 0).text()
        facture = self.facturemodel.getFactureById(facture_id)
    
        lignes_facture = self.ligneFactureModel.getAllLignesByFactureId(facture_id)

        self.view.display_facture_details(facture, lignes_facture)