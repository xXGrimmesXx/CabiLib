from app.backend.repository.patient_repository import PatientRepository
from app.backend.model.patient import Patient
from app.exceptions import RegleMetierException

class PatientService:
    @staticmethod
    def get_all_patients():
        return PatientRepository.get_all_patients()

    @staticmethod
    def get_patient_by_id(patient_id: int):
        return PatientRepository.get_patient_by_id(patient_id)

    @staticmethod
    def create_patient(patient: Patient) -> int:
        # VERIFICATION REGLE METIER
        if not patient.nom or not patient.prenom:
            raise RegleMetierException("Le nom et le prénom sont obligatoires pour créer un patient.")
        if len(PatientRepository.get_patients_by_acronyme(patient.acronyme)) > 0:
            raise RegleMetierException("L'acronyme doit être unique. Un patient avec cet acronyme existe déjà.")
        return PatientRepository.add_patient(patient)

    @staticmethod
    def update_patient(patient_id: int, updated_data: Patient):
        # VERIFICATION REGLE METIER
        if not updated_data.nom or not updated_data.prenom:
            raise RegleMetierException("Le nom et le prénom sont obligatoires lors de la modification.")
        if len(PatientRepository.get_patients_by_acronyme(updated_data.acronyme, exclude_id=patient_id)) > 0:
                raise RegleMetierException("L'acronyme doit être unique. Un autre patient avec cet acronyme existe déjà.")
        return PatientRepository.update_patient(patient_id, updated_data)

    @staticmethod
    def delete_patient(patient_id: int):
        # VERIFICATION REGLE METIER
        # (Ici on pourrait par exemple vérifier si le patient a des factures impayées)
        return PatientRepository.delete_patient(patient_id)