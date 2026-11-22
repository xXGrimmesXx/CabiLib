import os

from app.backend.services.ligneFacture_service import LigneFactureService
from app.backend.services.facture_service import FactureService
from app.backend.services.patient_service import PatientService
from app.frontend.views.suivre_facture_view import SuivreFactureView
from app.frontend.widgetPersonalise.error_boxes import ExceptionHandler
from app.exceptions import CabiLibException
from app.backend.model.facture import Facture
from app.backend.services.constantes_manager import get_constante
from os import environ, path, makedirs
import app.backend.services.facture_generator  as fg
import webbrowser
from shutil import copy
class SuivreFactureController:
    def __init__(self, model, view):
        self.view : SuivreFactureView= view

        # Connecter les signaux de la vue aux méthodes du controller
        self.view.facture_selected.connect(self.on_facture_selected)
        self.view.facture_updated.connect(self.on_facture_updated)
        self.view.search_changed.connect(self.on_search_changed)
        self.view.refresh.connect(self.on_refresh)
        self.view.reediter.connect(self.on_reediter)
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

    def on_facture_updated(self, facture: Facture):
        try:
            fac = FactureService().get_facture_by_id(facture.id)
            fac.date_paiement = facture.date_paiement
            fac.methode_paiement = facture.methode_paiement
            fac.description = facture.description
            fac.preuve_paiement = facture.preuve_paiement
            fac.regle = facture.regle
            fac.statut = facture.statut
            if self.view.preuve_paiement_file_path !="" :
                new_path = path.join(environ.get("APPDATA"),"CabiLib","PREUVES_PAIEMENT", facture.id + path.splitext(self.view.preuve_paiement_file_path)[1])
                if not path.exists(path.dirname(new_path)):
                    makedirs(path.dirname(new_path))
                if self.view.preuve_paiement_file_path != new_path:
                    copy(self.view.preuve_paiement_file_path, new_path)
                fac.preuve_paiement = new_path
            try:
                FactureService().update_facture(facture.id, fac.statut, fac.date_paiement, fac.description, fac.preuve_paiement)
            except CabiLibException as e:
                ExceptionHandler.handle(self.view, e)
            self.load_factures()  # Recharger les factures après la mise à jour
        except CabiLibException as e:
            ExceptionHandler.handle(self.view, e)

    def on_reediter(self, facture_id: str):
        
        facture = FactureService().get_facture_by_id(facture_id)
        patient = PatientService().get_patient_by_id(facture.patient_id)
        lfacs = LigneFactureService.get_lignes_by_facture_id(facture_id)
        basepath = get_constante("FACTURES_DIR")
        print(facture)
        fac_path = facture.start_date.strftime("%Y-%m")
        abs_dir = path.abspath(path.join(basepath, fac_path))
        if not path.exists(abs_dir):
            makedirs(abs_dir)
        filename = f"{facture.id+" "+(patient.acronyme if patient.acronyme is not None else '')}.pdf"
        abs_file = path.join(abs_dir, filename)
        annulation_factures = FactureService.get_factures_annule_by(facture_id)

        fp = fg.create_and_save(facture, patient, lfacs, annulation_factures,facture.start_date,facture.end_date,abs_file)
        if (fp is not None and path.exists(fp)):
            webbrowser.open_new(fp)
        
        