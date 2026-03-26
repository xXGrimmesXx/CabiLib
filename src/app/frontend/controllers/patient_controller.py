from app.backend.services.patient_service import PatientService
from app.exceptions import CabiLibException
from app.frontend.widgetPersonalise.error_boxes import ExceptionHandler

class PatientController:
    """CONTROLLER - Gère la logique entre le Model et la View via le Service"""
    
    def __init__(self, view):
        """
        Args:
            view: Instance de PatientView (interface)
        """
        self.view = view
        
        # Connecter les signaux de la vue aux méthodes du controller
        self.view.patient_selected.connect(self.on_patient_selected)
        self.view.patient_updated.connect(self.on_patient_updated)
        self.view.search_changed.connect(self.on_search_changed)
        self.view.patient_deleted.connect(self.on_patient_deleted)
        self.view.patient_created.connect(self.on_patient_created)
        self.view.refresh.connect(self.on_refresh)
        # Charger les données initiales
        self.load_patients()

    def on_refresh(self):
        self.load_patients()
    
    def load_patients(self):
        """Charger tous les patients depuis le modèle vers la vue"""
        try:
            self.view.load_patients(PatientService.get_all_patients())
        except CabiLibException as e:
            ExceptionHandler.handle(self.view, e)

    def on_patient_selected(self, row):
        """Gérer la sélection d'un patient dans la table"""
        try:
            # Récupérer les données de la ligne sélectionnée
            patient_id = self.view.patient_table.item(row, 0).text()
            patient = PatientService.get_patient_by_id(patient_id)

            # Afficher dans le formulaire
            self.view.display_patient_details(patient)
        except CabiLibException as e:
            ExceptionHandler.handle(self.view, e)
    
    def on_patient_updated(self, patient):
        """Gérer la mise à jour d'un patient"""
        try:
            row = self.view.get_selected_row()
            if row is not None:
                PatientService.update_patient(patient.id, patient)
                # Mettre à jour la table seulemen si ok
                self.view.update_table_row(row, patient)
        except CabiLibException as e:
            ExceptionHandler.handle(self.view, e)
    
    def on_search_changed(self, search_text):
        """Gérer le changement de texte dans la barre de recherche"""
        self.view.filter_rows(search_text)

    def on_patient_deleted(self, patient_id):
        """Gérer la suppression d'un patient"""
        try:
            PatientService.delete_patient(patient_id)
            self.load_patients()
            self.view.clear_inputs()
        except CabiLibException as e:
            ExceptionHandler.handle(self.view, e)

    def on_patient_created(self, patient):
        """Gérer la création d'un nouveau patient"""
        try:
            patient_id = PatientService.create_patient(patient)
            if patient_id:
                # Recharger la liste des patients
                self.load_patients()
                self.view.clear_inputs()
        except CabiLibException as e:
            ExceptionHandler.handle(self.view, e)
