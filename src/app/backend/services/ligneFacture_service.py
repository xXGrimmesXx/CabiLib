from app.backend.repository.ligne_facture_repository import LigneFactureRepository
from app.backend.model.ligneFacture import LigneFacture
from app.exceptions import RegleMetierException

class LigneFactureService:
    @staticmethod
    def get_all_lignes():
        return LigneFactureRepository.get_all_lignes()

    @staticmethod
    def get_ligne(id_facture: str, id_rdv: int):
        return LigneFactureRepository.get_ligne(id_facture, id_rdv)

    @staticmethod
    def add_ligne(ligne: LigneFacture):
        # REGLE METIER
        if ligne.montant_facture is not None and ligne.montant_facture < 0:
            raise RegleMetierException("Le montant d'une ligne de facture ne peut pas être négatif.")
        return LigneFactureRepository.add_ligne(ligne)

    @staticmethod
    def delete_ligne(id_facture: str, id_rdv: int):
        return LigneFactureRepository.delete_ligne(id_facture, id_rdv)

    @staticmethod
    def get_lignes_by_facture_id(id_facture: str):
        return LigneFactureRepository.get_lignes_by_facture_id(id_facture)

    @staticmethod
    def get_lignes_by_patient_id(patient_id: int):
        return LigneFactureRepository.get_lignes_by_patient_id(patient_id)

    @staticmethod
    def get_lignes_by_rdv_id(id_rdv: int):
        return LigneFactureRepository.get_lignes_by_rdv_id(id_rdv)