class PatientController:
    """CONTROLLER - Gère la logique entre le Model et la View"""
    
    def __init__(self, model, view):
        """
        Args:
            model: Classe Patient (modèle de données)
            view: Instance de PatientView (interface)
        """
        self.model = model
        self.view = view
        
        # Connecter les signaux de la vue aux méthodes du controller
        self.view.patient_selected.connect(self.on_patient_selected)
        self.view.patient_updated.connect(self.on_patient_updated)
        self.view.search_changed.connect(self.on_search_changed)
        self.view.patient_deleted.connect(self.on_patient_deleted)
        self.view.patient_created.connect(self.on_patient_created)
        
        # Charger les données initiales
        self.load_patients()
    
    def load_patients(self):
        """Charger tous les patients depuis le modèle vers la vue"""
        # Récupérer les patients depuis le modèle
        patients_objects = self.model.getAllPatients()
        
        # Charger dans la vue
        self.view.load_patients(patients_objects)
    
    def on_patient_selected(self, row):
        """Gérer la sélection d'un patient dans la table"""
        # Récupérer les données de la ligne sélectionnée
        patient_id = self.view.patient_table.item(row, 0).text()
        patient = self.model.getPatientById(patient_id)

        # Afficher dans le formulaire
        self.view.display_patient_details(patient)
    
    def on_patient_updated(self, patient):
        """Gérer la mise à jour d'un patient"""
        row = self.view.get_selected_row()
        if row is not None:
            # Mettre à jour la table
            self.view.update_table_row(row, patient)
            
            self.model.updatePatient(patient.id, patient)
    
    def on_search_changed(self, search_text):
        """Gérer le changement de texte dans la barre de recherche"""
        self.view.filter_rows(search_text)

    def on_patient_deleted(self, patient_id):
        """Gérer la suppression d'un patient"""
        self.model.deletePatient(patient_id)
        self.view.load_patients(self.model.getAllPatients())

    def on_patient_created(self, patient):
        """Gérer la création d'un nouveau patient"""
        patient_id = self.model.addPatient(patient)
        if patient_id:
            # Recharger la liste des patients
            self.view.load_patients(self.model.getAllPatients())
