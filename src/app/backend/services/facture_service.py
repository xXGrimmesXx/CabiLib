from datetime import datetime, date
from app.backend.repository.facture_repository import FactureRepository
from app.backend.model.facture import Facture
from app.exceptions import RegleMetierException
from app.backend.services.ligneFacture_service import LigneFactureService

class FactureService:
    def __init__(self):
        pass

    def get_all_factures(self) -> list[Facture]:
        return FactureRepository.get_all_factures()

    @staticmethod
    def get_facture_by_id(facture_id: str) -> Facture | None:
        return FactureRepository.get_facture_by_id(facture_id)

    @staticmethod
    def add_facture(facture: Facture) -> str:
        # REGLE METIER
        if facture.patient_id is None or facture.patient_id <= 0:
            raise RegleMetierException("ID patient invalide.")
        if facture.statut not in ["IMPAYE", "PAYE", "ANNULE"]:
            raise RegleMetierException(f"Statut inconnu: {facture.statut}")
        return FactureRepository.add_facture(facture)

    @staticmethod
    def update_facture(facture_id: str, new_statut: str = "IMPAYE", date_paiement: date = None, description: str = None) -> None:
        # REGLE METIER
        if new_statut == "PAYE" and not date_paiement:
            date_paiement = datetime.today().date()
        return FactureRepository.update_facture_status(facture_id, new_statut, date_paiement)

    @staticmethod
    def delete_facture(facture_id: str) -> None:
        # REGLE METIER : On interdit la suppression si la facture est déjà acquittée
        facture = FactureRepository.get_facture_by_id(facture_id)
        if facture and facture.statut == "PAYE":
            raise RegleMetierException("Impossible de supprimer une facture déjà payée.")
        return FactureRepository.delete_facture(facture_id)

    @staticmethod
    def get_factures_impaye_by_patient_id(patient_id: int) -> list[Facture]:
        return FactureRepository.get_factures_impaye_by_patient_id(patient_id)

    @staticmethod
    def generate_numero_facture(date_emission: date=None) -> str:
        # Générer un numéro de facture unique basé sur la date et un compteur
        num =  FactureRepository.generate_numero_facture(date_emission)
        return num

    @staticmethod
    def get_factures_annule_by(facture_id: str) -> list[Facture]:

        lignes = LigneFactureService.get_lignes_by_facture_id(facture_id)
        annulation_factures = {}
        rdvs = {}
        for ligne in lignes:
            rdvs[ligne.idRendezVous] = LigneFactureService.get_lignes_by_rdv_id(ligne.idRendezVous)
        keys = rdvs.keys()
        for key in keys:
            for ligne in rdvs[key]:
                if inf(ligne.idFacture, facture_id) and ligne.idFacture not in annulation_factures:
                    if not key in annulation_factures.keys() or inf(annulation_factures[key], ligne.idFacture):
                        annulation_factures[key] = ligne.idFacture
        return [annulation_factures[key] for key in annulation_factures.keys()]

def inf(facture_id1: str, facture_id2: str) -> bool:
    # Compare les numéros de facture en fonction de la date et du compteur
    # Format attendu : "YYYYMMDD-XXXX"
    fac,year1,month1, compteur1 = facture_id1.split('-')
    fac,year2,month2, compteur2= facture_id2.split('-')
    year1, month1 = int(year1), int(month1)
    year2, month2 = int(year2), int(month2)

    if year1 < year2:
        return True
    elif year1 == year2 and month1 < month2:
        return True
    elif year1 == year2 and month1 == month2:
        return int(compteur1) < int(compteur2)
    else:
        return False

