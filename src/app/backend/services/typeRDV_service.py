from app.backend.repository.type_rdv_repository import TypeRDVRepository
from app.backend.model.typeRDV import TypeRDV
from app.exceptions import RegleMetierException

class TypeRDVService:
    @staticmethod
    def get_all_types():
        return TypeRDVRepository.get_all_types()

    @staticmethod
    def get_type_by_id(type_id: int):
        return TypeRDVRepository.get_type_by_id(type_id)

    @staticmethod
    def add_type(type_rdv: TypeRDV):
        # REGLE METIER
        if type_rdv.prix is not None and type_rdv.prix < 0:
            raise RegleMetierException("Le prix d'un type de rendez-vous ne peut pas être inférieur à 0.")
        if type_rdv.duree_minutes <= 0:
            raise RegleMetierException("La durée d'un type de rendez-vous doit être strictement positive.")
        return TypeRDVRepository.add_type(type_rdv)

    @staticmethod
    def update_type(updated_data: TypeRDV):
        # REGLE METIER
        if updated_data.prix is not None and updated_data.prix < 0:
            raise RegleMetierException("Le prix ne peut pas être inférieur à 0.")
        if updated_data.duree_minutes <= 0:
            raise RegleMetierException("La durée doit être strictement positive.")
        return TypeRDVRepository.update_type(updated_data)

    @staticmethod
    def delete_type(type_rdv_id: int):
        # REGLE METIER : Protection de l'intégrité de la base de données
        if TypeRDVRepository.has_linked_rendezvous(type_rdv_id):
            raise RegleMetierException("Impossible de supprimer ce type de RDV car des rendez-vous y sont actuellement rattachés.")
        return TypeRDVRepository.delete_type(type_rdv_id)