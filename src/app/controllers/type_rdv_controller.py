from app.views.type_rdv_view import TypeRDVView
from app.model.typeRDV import TypeRDV

class TypeRDVController:
    def __init__(self, model_class, view):
        self.model_class = model_class
        self.view = view
        self.load_types_rdv()
        
        # Connecter les signaux
        self.view.type_rdv_selected.connect(self.on_type_rdv_selected)
        self.view.type_rdv_updated.connect(self.on_type_rdv_updated)
        self.view.type_rdv_created.connect(self.on_type_rdv_created)
        self.view.refresh.connect(self.on_refresh)

    def on_refresh(self):
        self.load_types_rdv()
    
    def load_types_rdv(self):
        """Charger tous les types de RDV"""
        types_rdv = TypeRDV.getAllTypesRDV()
        self.view.load_types_rdv(types_rdv)
    
    def on_type_rdv_selected(self, row):
        """Gérer la sélection d'un type de RDV"""
        type_rdv_id = int(self.view.type_rdv_table.item(row, 0).text())
        type_rdv = TypeRDV.getTypeRDVById(type_rdv_id)
        if type_rdv:
            self.view.display_type_rdv_details(type_rdv)
    
    def on_type_rdv_updated(self, type_rdv):
        """Mettre à jour un type de RDV"""
        if type_rdv.id:
            TypeRDV.updateTypeRDV(type_rdv)
            self.load_types_rdv()
    
    def on_type_rdv_created(self, type_rdv):
        """Créer un nouveau type de RDV"""
        TypeRDV.addTypeRDV(type_rdv)
        self.load_types_rdv()