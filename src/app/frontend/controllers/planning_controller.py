from PySide6.QtCore import QObject, QTime
import traceback
from datetime import timedelta
from app.backend.model.rendezVous import RendezVous
from app.frontend.views.planning_view import PlanningView
from app.backend.services.rendezVous_service import RendezVousService
from app.backend.services.patient_service import PatientService
from app.backend.services.typeRDV_service import TypeRDVService
from app.backend.services.ligneFacture_service import LigneFactureService
from app.exceptions import CabiLibException
from app.frontend.widgetPersonalise.error_boxes import ExceptionHandler
from app.backend.services import constantes_manager as cm

class PlanningController(QObject):
    """Contrôleur pour gérer le planning des rendez-vous"""

    def __init__(self, view: PlanningView):
        super().__init__()  # Initialiser QObject
        self.view = view
        
        self.current_week_start = self.view.get_current_week_start()
        
        try:
            self.view.set_liste_patients(PatientService.get_all_patients())
            self.view.set_liste_type_rdv(TypeRDVService.get_all_types())
            
            # Connecter les signaux
            self.view.creer_clicked.connect(self.on_creer_clicked)
            self.view.supprimer_clicked.connect(self.on_supprimer_clicked)
            self.view.previous_week_clicked.connect(self.on_previous_week)
            self.view.next_week_clicked.connect(self.on_next_week)
            self.view.cell_clicked.connect(self.on_cell_clicked)
            self.view.refresh.connect(self.on_refresh)
            self.view.type_rdv_changed.connect(self.on_type_rdv_changed)
            
            # Charger les données initiales
            self.load_week_rdvs()
        except CabiLibException as e:
            ExceptionHandler.handle(self.view, e)

    def on_refresh(self):
        """Met à jour la liste des patients ainsi que les types de RDV et recharge les RDV de la semaine"""
        try:
            self.load_week_rdvs()
            self.view.set_liste_patients(PatientService.get_all_patients())
            self.view.set_liste_type_rdv(TypeRDVService.get_all_types())
        except CabiLibException as e:
            ExceptionHandler.handle(self.view, e)
    
    def on_previous_week(self):
        """Naviguer vers la semaine précédente"""
        self.current_week_start -= timedelta(days=7)
        self.load_week_rdvs()
    
    def on_next_week(self):
        """Naviguer vers la semaine suivante"""
        try :
            self.current_week_start += timedelta(days=7)
            self.load_week_rdvs()
        except Exception as e:
            print(f"Error in on_next_week: {e}")
            traceback.print_exc()
    
    def on_cell_clicked(self, day_index: int, time_slot: str) -> None:
        """Gérer le clic sur une cellule du planning
        Args:
            day_index (int): Index du jour (0=Lundi, 6=Dimanche)
            time_slot (str): Heure au format "HH:MM"
        """
        try:
            # Calculer la date exacte
           
            days = day_index
            hours = int(time_slot.split(":")[0])
            minutes = int(time_slot.split(":")[1])
            
            date = self.current_week_start + timedelta(days=days, hours=hours, minutes=minutes)
            rendez_vous = RendezVousService.get_rendezvous_by_datetime(date)
            print(f"Rendez-vous trouvés pour {date}: \n{rendez_vous}")
            if (rendez_vous is not None and rendez_vous!=[]):
                self.view.rdvs_selectionne = rendez_vous
                self.view.afficher_details_rdv()
                self.view.show_rdv_onglet()
                
                
            else:
                self.view.on_clear_clicked()
                self.view.rdvs_selectionne = [RendezVous(id=None, date=date, patient_id=None, type_id=None, motif=None, presence=None, google_calendar_id=None)]
                self.view.afficher_details_rdv()
                self.view.show_rdv_onglet()
        except CabiLibException as e:
            ExceptionHandler.handle(self.view, e)
    
    def load_week_rdvs(self) -> None:
        """Charger les rendez-vous de la semaine"""
        try:
            # Calculer le début et la fin de la semaine (Lundi à Dimanche)
            week_start = self.current_week_start
            week_end = week_start + timedelta(days=6, hours=23, minutes=59)  # Dimanche

            # Mettre à jour le label
            self.view.set_week_label(week_start, week_end)
            # Effacer le planning
            self.view.clear_planning()
            # Récupérer les RDV de la semaine depuis la base de données
            rdvs = RendezVousService.get_rendezvous_by_plage(week_start, week_end)
            if (rdvs is not None and rdvs!=[]):
                # Ajouter les RDV au planning
                for rdv in rdvs:
                    if (rdv is None):
                        continue
                    patient = PatientService.get_patient_by_id(rdv.patient_id)
                    rdv_type = TypeRDVService.get_type_by_id(rdv.type_id)
                    if patient is None:
                        continue
                    if rdv_type is None:
                        continue
                    self.view.add_rdv_to_planning(rdv, patient, rdv_type)
        except CabiLibException as e:
            ExceptionHandler.handle(self.view, e)

    def on_creer_clicked(self, rdvs: list[RendezVous]):
        """Gérer la création ou la modification d'un rendez-vous"""
        try:
            if rdvs is None or len(rdvs) == 0:
                self.view.afficher_champs_obligatoires()
                return
            for rdv in rdvs:
                if (rdv is None):
                    self.view.afficher_champs_obligatoires()
                    return
                elif( rdv.patient_id is None or rdv.date is None or rdv.type_id is None or rdv.presence is None):
                    self.view.afficher_champs_obligatoires()
                    return
                
                # Laissons le service s'occuper de la vérification de créneau (laissera passer une exception si conflit)
                if(rdv.id is None):
                    if (rdv.date and rdv.patient_id and rdv.type_id):
                        RendezVousService.add_rendezvous(rdv)
                    else :
                        self.view.afficher_champs_obligatoires()
                        return
                else :
                    # Pas encore implémenté en service l'update global, mais imaginons
                    RendezVousService.update_rendezvous(rdv.id, rdv)
                
            # Recharger la semaine actuelle
            self.load_week_rdvs()
        except CabiLibException as e:
            ExceptionHandler.handle(self.view, e)

    def on_supprimer_clicked(self, rdv):
        """Gérer la suppression d'un rendez-vous"""
        try:
            if rdv.id is not None:
                factures = LigneFactureService.get_lignes_by_rdv_id(rdv.id)
                if factures is not None and len(factures) > 0:
                    self.view.erreur_suppression_rdv_facture()
                    return
                RendezVousService.delete_rendezvous(rdv.id)
                self.load_week_rdvs()
        except CabiLibException as e:
            ExceptionHandler.handle(self.view, e)

    def on_type_rdv_changed(self, type_id: int):
        """Gérer le changement de type de rendez-vous dans le formulaire"""
        try:
            if type_id is not None and type_id != -1:
                rdv_type = TypeRDVService.get_type_by_id(type_id)
                if rdv_type is not None:
                    heure_max_str = cm.get_constante("HEURE_FIN")
                    heure_max = QTime.fromString(heure_max_str, "HH:mm")
                    heure_max = heure_max.addSecs(-rdv_type.duree.seconds)  # Soustraire la durée du RDV
                    print(f"Type de RDV sélectionné: {rdv_type.nom}, durée: {-rdv_type.duree.seconds/60} minutes, heure max pour le créneau: {heure_max.toString('HH:mm')}")
                    self.view.time_input.setMaximumTime(heure_max)

        except CabiLibException as e:
            ExceptionHandler.handle(self.view, e)