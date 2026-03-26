from datetime import datetime, date
from app.backend.repository.facture_repository import FactureRepository
from app.backend.model.facture import Facture
from app.exceptions import RegleMetierException

class FactureService:
    def __init__(self):
        pass

    def get_all_factures(self) -> list[Facture]:
        return FactureRepository.get_all_factures()

    def get_facture_by_id(self, facture_id: str) -> Facture | None:
        return FactureRepository.get_facture_by_id(facture_id)

    def add_facture(self, patient_id: int, date_emission: date = None, description: str = "", statut: str = "IMPAYE", date_paiement: date = None) -> str:
        # REGLE METIER
        if patient_id is None or patient_id <= 0:
            raise RegleMetierException("ID patient invalide.")
        if statut not in ["IMPAYE", "PAYE", "ANNULE"]:
            raise RegleMetierException(f"Statut inconnu: {statut}")
        return FactureRepository.add_facture(patient_id, date_emission, description, statut, date_paiement)

    def update_facture_status(self, facture_id: str, new_statut: str = "IMPAYE", date_paiement: date = None) -> None:
        # REGLE METIER
        if new_statut == "PAYE" and not date_paiement:
            date_paiement = datetime.today().date()
        return FactureRepository.update_facture_status(facture_id, new_statut, date_paiement)

    def delete_facture(self, facture_id: str) -> None:
        # REGLE METIER : On interdit la suppression si la facture est déjà acquittée
        facture = FactureRepository.get_facture_by_id(facture_id)
        if facture and facture.statut == "PAYE":
            raise RegleMetierException("Impossible de supprimer une facture déjà payée.")
        return FactureRepository.delete_facture(facture_id)

    def get_factures_impaye_by_patient_id(self, patient_id: int) -> list[Facture]:
        return FactureRepository.get_factures_impaye_by_patient_id(patient_id)