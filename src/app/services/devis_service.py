from datetime import date
from app.backend.model.devis import Devis
from app.backend.repository.devis_repository import DevisRepository
from app.exceptions import RegleMetierException

class DevisService:
    def __init__(self):
        pass

    def get_all_devis(self) -> list[Devis]:
        return DevisRepository.get_all_devis()

    @staticmethod
    def get_devis_by_id(devis_id: str) -> Devis | None:
        return DevisRepository.get_devis_by_id(devis_id)

    @staticmethod
    def add_devis(devis: Devis) -> str:
        # REGLE METIER
        if devis.patient_id is None or devis.patient_id <= 0:
            raise RegleMetierException("ID patient invalide.")
        return DevisRepository.add_devis(devis)

    @staticmethod
    def delete_devis(devis_id: str) -> None:
        # REGLE METIER : On interdit la suppression si le devis est déjà acquitté
        devis = DevisRepository.get_devis_by_id(devis_id)
        if devis and devis.statut == "PAYE":
            raise RegleMetierException("Impossible de supprimer un devis déjà payé.")
        return DevisRepository.delete_devis(devis_id)

    @staticmethod
    def generate_numero_devis(date_emission: date=None) -> str:
        # Générer un numéro de devis unique basé sur la date et un compteur
        num =  DevisRepository.generate_numero_devis(date_emission)
        return num
