from PySide6.QtCore import QObject
from datetime import timedelta
from app.model.patient import Patient
from app.model.typeRDV import TypeRDV
from app.model.rendezVous import RendezVous
from app.views.planning_view import PlanningView

class PlanningController(QObject):
    """Contrôleur pour gérer le planning des rendez-vous"""

    def __init__(self, model: RendezVous, view:PlanningView):
        super().__init__()  # Initialiser QObject
        self.rendez_vous_model = model  # RendezVous
        self.patient_model: Patient= Patient
        self.type_rendez_vous: TypeRDV = TypeRDV
        self.view = view
        self.current_week_start = self.view.get_current_week_start()
        self.view.set_liste_patients(self.patient_model.getAllPatients())
        self.view.set_liste_type_rdv(self.type_rendez_vous.getAllTypesRDV())
        
        # Connecter les signaux
        self.view.creer_clicked.connect(self.on_creer_clicked)
        self.view.supprimer_clicked.connect(self.on_supprimer_clicked)
        self.view.previous_week_clicked.connect(self.on_previous_week)
        self.view.next_week_clicked.connect(self.on_next_week)
        self.view.cell_clicked.connect(self.on_cell_clicked)
        self.view.refresh.connect(self.on_refresh)
        # Charger les données initiales
        self.load_week_rdvs()

    def on_refresh(self):
        """Met à jour la liste des patients ainsi que les types de RDV et recharge les RDV de la semaine"""
        self.load_week_rdvs()
        self.view.set_liste_patients(self.patient_model.getAllPatients())
        self.view.set_liste_type_rdv(self.type_rendez_vous.getAllTypesRDV())
    
    def on_previous_week(self):
        """Naviguer vers la semaine précédente"""
        self.current_week_start -= timedelta(days=7)
        print(self.current_week_start)
        self.load_week_rdvs()
        print("fin de on previous week")
    
    def on_next_week(self):
        """Naviguer vers la semaine suivante"""
        try :
            self.current_week_start += timedelta(days=7)
            self.load_week_rdvs()
            print("fin de on next week")
        except Exception as e:
            print(f"Error in on_next_week: {e}")
    
    def on_cell_clicked(self, day_index: int, time_slot: str) -> None:
        """Gérer le clic sur une cellule du planning
        Args:
            day_index (int): Index du jour (0=Lundi, 6=Dimanche)
            time_slot (str): Heure au format "HH:MM"
        """
        
        # Calculer la date exacte
       
        days = day_index
        hours = int(time_slot.split(":")[0])
        minutes = int(time_slot.split(":")[1])
        
        date = self.current_week_start + timedelta(days=days, hours=hours, minutes=minutes)
        rendez_vous = self.rendez_vous_model.getRendezVousByDateTime(date)
        if (rendez_vous is not None and rendez_vous!=[]):
            self.view.rdvs_selectionne = rendez_vous
            self.view.afficher_details_rdv()
            self.view.show_rdv_onglet()
            
            
        else:
            self.view.on_clear_clicked()
            self.view.rdvs_selectionne = [RendezVous(None, date, None, None, None, None, None)]
            self.view.afficher_details_rdv()
            self.view.show_rdv_onglet()
    
    def load_week_rdvs(self) -> None:
        """Charger les rendez-vous de la semaine"""
        # Calculer le début et la fin de la semaine (Lundi à Dimanche)
        week_start = self.current_week_start
        week_end = week_start + timedelta(days=6)  # Dimanche

        # Mettre à jour le label
        self.view.set_week_label(week_start, week_end)
        # Effacer le planning
        self.view.clear_planning()
        # Récupérer les RDV de la semaine depuis la base de données
        rdvs = self.rendez_vous_model.getRendezVousByPlage(week_start, week_end)
        if (rdvs is not None and rdvs!=[]):
            # Ajouter les RDV au planning
            for rdv in rdvs:
                if (rdv is None):
                    continue
                patient = self.patient_model.getPatientById(rdv.patient_id)
                rdv_type = self.type_rendez_vous.getTypeRDVById(rdv.type_id)
                if patient is None:
                    continue
                if rdv_type is None:
                    continue
                self.view.add_rdv_to_planning(rdv, patient, rdv_type)

    def on_creer_clicked(self, rdv):
        """Gérer la création ou la modification d'un rendez-vous"""
        if (rdv is None):
            self.view.afficher_champs_obligatoires()
            return
        elif( rdv.patient_id is None or rdv.date is None or rdv.type_id is None or rdv.presence is None):
            self.view.afficher_champs_obligatoires()
            return
        elif not self.rendez_vous_model.creneauLibre(rdv):
            self.view.afficher_creneau_indisponible()
            return
        
        if(rdv.id is None):
            if (rdv.date and rdv.patient_id and rdv.type_id):
                self.rendez_vous_model.addRendezVous(rdv)
            else :
                self.view.afficher_champs_obligatoires()
                return
        else :
            self.rendez_vous_model.updateRendezVous(rdv.id, rdv)
        
        # Recharger la semaine actuelle
        self.load_week_rdvs()

    def on_supprimer_clicked(self, rdv):
        """Gérer la suppression d'un rendez-vous"""
        if rdv.id is not None:
            self.rendez_vous_model.deleteRendezVous(rdv.id)
            self.load_week_rdvs()