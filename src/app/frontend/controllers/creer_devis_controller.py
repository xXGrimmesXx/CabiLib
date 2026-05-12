from os import path,environ,makedirs

from datetime import timedelta, datetime
import webbrowser

from app.backend.model.patient import Patient
from app.backend.model.devis import Devis
from app.backend.model.acte_devis import ActeDevis

from app.backend.services.patient_service import PatientService
from app.backend.services.typeRDV_service import TypeRDVService
from app.backend.services.devis_service import DevisService
from app.backend.services.actedevis_service import ActeDevisService
from app.backend.services.devis_generator import create_and_save
from app.backend.services.constantes_manager import get_constante


from app.frontend.views.creer_devis_view import CreerDevisView
from app.exceptions import CabiLibException, EntiteIntrouvableException, RegleMetierException
from app.frontend.widgetPersonalise.error_boxes import ExceptionHandler


class CreerDevisController:
    def __init__(self, model, view: CreerDevisView):
    
        self.view: CreerDevisView = view
        # Connecter les signaux de la vue aux méthodes du contrôleur
        self.view.devis_generer.connect(self.on_devis_generer)
        self.view.devis_preview.connect(self.on_devis_preview)
        self.view.refresh_sig.connect(self.on_refresh)
        self.on_refresh()

    def on_refresh(self):
        print("CreerDevisController: Refreshing data...")
        self.view.set_patient_list(PatientService.get_all_patients())
        self.view.refresh_actes(TypeRDVService.get_all_types())

    def on_devis_generer(self, id_patient: int, date_debut: datetime, date_fin: datetime, actes_qtt: list[tuple[int, float]]):
        """Générer un devis pour un patient spécifique entre deux dates.
        args:
            id_patient (int): L'identifiant du patient.
            date_debut (datetime): La date de début.
            date_fin (datetime): La date de fin.
            actes_qtt (list[tuple[int, float]]): La liste des actes eturs quantités.
        """
        try:
            self.editer_devis(id_patient, date_debut, date_fin, actes_qtt, preview=False)
        except CabiLibException as e:
            ExceptionHandler.handle(self.view, e)
        except Exception as e:
            ExceptionHandler.handle(self.view, e)

    

    def on_devis_preview(self, id_patient: int, date_debut: datetime, date_fin: datetime, actes_qtt: list[tuple[int, float]]):
        """Prévisualiser un devis pour un patient spécifique entre deux dates.
        args:
            id_patient (int): L'identifiant du patient.
            date_debut (datetime): La date de début.
            date_fin (datetime): La date de fin.
            actes_qtt (list[tuple[int, float]]): La liste des actes et leurs quantités.
        """
        try:
            self.editer_devis(id_patient, date_debut, date_fin, actes_qtt, preview=True)
        except CabiLibException as e:
            ExceptionHandler.handle(self.view, e)
        except Exception as e:
            ExceptionHandler.handle(self.view, e)


    def editer_devis(self, id_patient: int, date_debut: datetime, date_fin: datetime, actes_qtt: list[tuple[int, float]], preview=False) -> tuple[int, str]:
        """Générer un devis pour un patient spécifique entre deux dates.
        args:
            id_patient (int): L'identifiant du patient.
            date_debut (datetime): La date de début.
            date_fin (datetime): La date de fin.
            actes_qtt (list[tuple[int, float]]): La liste des actes et leurs quantités.
        Returns:
            tuple[int, str]: Un tuple contenant l'identifiant de la facture créée et le chemin du fichier PDF généré.
        """
        patient = PatientService.get_patient_by_id(id_patient)
        devis = Devis(patient_id=patient.id, date_debut=date_debut, date_fin=date_fin, id=DevisService.generate_numero_devis(datetime.now()))
        actes = []
        for id_type_rdv, qtt in actes_qtt.items():
            actes.append(ActeDevis(id_devis =devis.id, id_type_rdv=id_type_rdv, quantite= qtt))

        if not preview:
            DevisService.add_devis(devis)
            for acte in actes:
                ActeDevisService.add_acte(acte)
        
        save_path = get_constante("DEVIS_DIR")
        if not path.exists(save_path):
            makedirs(save_path)
        save_path = path.join(save_path, f"{devis.id}.pdf")
        
        pdf_path = create_and_save(devis, actes, patient, save_path, open_files=True)