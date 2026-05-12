from app.backend.model.acte_devis import ActeDevis
from app.backend.repository.actedevis_repository import ActeDevisRepository

class ActeDevisService:
    def __init__(self):
        pass

    def get_all_actes(self) -> list[ActeDevis]:
        return ActeDevisRepository.get_all_actes()

    @staticmethod
    def get_acte_by_id(devis_id: str, type_rdv_id: int) -> ActeDevis | None:
        return ActeDevisRepository.get_acte_by_id(devis_id, type_rdv_id)
    
    @staticmethod
    def get_actes_by_devis_id(devis_id: str) -> list[ActeDevis]:
        return ActeDevisRepository.get_actes_by_devis_id(devis_id)

    @staticmethod
    def add_acte(acte: ActeDevis) -> tuple[str, int]:
        if acte is None:
            raise ValueError("L'acte ne peut pas être None.")
        if acte.id_devis is None:
            raise ValueError("L'identifiant du devis ne peut pas être None.")
        if acte.id_type_rdv is None:
            raise ValueError("L'identifiant du type de RDV ne peut pas être None.")
        if acte.quantite is None:
            raise ValueError("La quantité ne peut pas être None.")
        if acte.quantite <= 0:
            raise ValueError("La quantité doit être supérieure à zéro.")
        return ActeDevisRepository.add_acte(acte)
        

    @staticmethod
    def delete_acte(devis_id: str, type_rdv_id: int) -> None:
        # REGLE METIER : On interdit la suppression si le devis est déjà acquitté
        acte = ActeDevisRepository.get_acte_by_id(devis_id, type_rdv_id)
        if acte:
            ActeDevisRepository.delete_acte(devis_id, type_rdv_id)
