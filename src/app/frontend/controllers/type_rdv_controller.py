from app.backend.services.typeRDV_service import TypeRDVService
from app.exceptions import CabiLibException
from app.frontend.widgetPersonalise.error_boxes import ExceptionHandler

class TypeRDVController:
    def __init__(self, view):
        self.view = view
        self.load_types_rdv()
        
        # Connecter les signaux
        self.view.type_rdv_selected.connect(self.on_type_rdv_selected)
        self.view.type_rdv_updated.connect(self.on_type_rdv_updated)
        self.view.type_rdv_created.connect(self.on_type_rdv_created)
        self.view.type_rdv_deleted.connect(self.on_type_rdv_deleted)
        self.view.refresh.connect(self.on_refresh)

    def on_refresh(self):
        self.load_types_rdv()
    
    def load_types_rdv(self):
        """Charger tous les types de RDV"""
        try:
            types_rdv = TypeRDVService.get_all_types()
            self.view.load_types_rdv(types_rdv)
        except CabiLibException as e:
            ExceptionHandler.handle(self.view, e)
    
    def on_type_rdv_selected(self, row):
        """Gérer la sélection d'un type de RDV"""
        try:
            type_rdv_id = int(self.view.type_rdv_table.item(row, 0).text())
            type_rdv = TypeRDVService.get_type_by_id(type_rdv_id)
            if type_rdv:
                self.view.display_type_rdv_details(type_rdv)
        except CabiLibException as e:
            ExceptionHandler.handle(self.view, e)
    
    def on_type_rdv_updated(self, type_rdv):
        """Mettre à jour un type de RDV"""
        if type_rdv.id:
            try:
                TypeRDVService.update_type(type_rdv)
                self.load_types_rdv()
            except CabiLibException as e:
                ExceptionHandler.handle(self.view, e)
    
    def on_type_rdv_created(self, type_rdv):
        """Créer un nouveau type de RDV"""
        try:
            TypeRDVService.add_type(type_rdv)
            self.load_types_rdv()
        except CabiLibException as e:
            ExceptionHandler.handle(self.view, e)

    def on_type_rdv_deleted(self, type_rdv_id):
        """Supprimer un type de RDV"""
        if type_rdv_id:
            try:
                TypeRDVService.delete_type(type_rdv_id)
                self.load_types_rdv()
            except CabiLibException as e:
                ExceptionHandler.handle(self.view, e)
            
        