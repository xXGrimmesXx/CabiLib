from datetime import datetime, timedelta
from app.backend.repository.rendezvous_repository import RendezVousRepository
from app.backend.model.rendezVous import RendezVous
from app.exceptions import RegleMetierException, ConflitHoraireException

class RendezVousService:

    @staticmethod
    def get_all_rendezvous():
        return RendezVousRepository.get_all_rendezvous()

    @staticmethod
    def get_rendezvous_by_id(rdv_id: int):
        return RendezVousRepository.get_rendezvous_by_id(rdv_id)

    @staticmethod
    def get_rendezvous_by_patient_id(patient_id: int):
        return RendezVousRepository.get_rendezvous_by_patient_id(patient_id)

    @staticmethod
    def get_rendezvous_by_plage(date_debut: datetime, date_fin: datetime):
        return RendezVousRepository.get_rendezvous_by_plage(date_debut, date_fin)

    @staticmethod
    def get_rendezvous_by_datetime(exact_date: datetime):
        return RendezVousRepository.get_rendezvous_by_datetime(exact_date)

    @staticmethod
    def get_rendezvous_by_patient_and_date_range(patient_id: int, start_date: datetime, end_date: datetime):
        return RendezVousRepository.get_rendezvous_by_patient_and_date_range(patient_id, start_date, end_date)

    @staticmethod
    def get_rendezvous_by_facture_id(facture_id: str):
        return RendezVousRepository.get_rendezvous_by_facture_id(facture_id)

    @staticmethod
    def add_rendezvous(rdv: RendezVous):
        # REGLES METIER
        if not rdv.patient_id or not rdv.type_id:
            raise RegleMetierException("Le rendez-vous doit obligatoirement être lié à un patient et avoir un type.")
            
        if not RendezVousRepository.creneau_libre(rdv):
            raise ConflitHoraireException("Conflit d'horaire : Le créneau horaire est déjà occupé.")

        return RendezVousRepository.add_rendezvous(rdv)

    @staticmethod
    def update_rendezvous(rdv_id: int, new_rdv: RendezVous):
        if not new_rdv.patient_id or not new_rdv.type_id:
            raise RegleMetierException("Le rendez-vous doit obligatoirement être lié à un patient et avoir un type.")
            
        if not RendezVousRepository.creneau_libre(new_rdv):
            raise ConflitHoraireException("Conflit d'horaire : Le créneau horaire est déjà occupé.")
            
        return RendezVousRepository.update_rendezvous(rdv_id, new_rdv)

    @staticmethod
    def delete_rendezvous(rdv_id: int):
        return RendezVousRepository.delete_rendezvous(rdv_id)