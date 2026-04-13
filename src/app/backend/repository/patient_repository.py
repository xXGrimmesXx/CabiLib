from app.backend.database.database import SessionLocal
from app.backend.model.patient import Patient
from app.exceptions import DatabaseException,EntiteIntrouvableException
from sqlalchemy.exc import SQLAlchemyError

class PatientRepository:
    """SERVICE - Contient la logique d'accès aux données pour l'entité Patient"""

    @staticmethod
    def get_all_patients():
        with SessionLocal() as db:
            try:
                return db.query(Patient).all()
            except SQLAlchemyError as e:
                raise DatabaseException(f"Erreur lors de la récupération des patients: {str(e)}")

    @staticmethod
    def get_patient_by_id(patient_id: int):
        with SessionLocal() as db:
            try:
                patient = db.get(Patient, int(patient_id))
                if not patient:
                    raise EntiteIntrouvableException("Patient non trouvé")
                return patient
            except SQLAlchemyError as e:
                raise DatabaseException(f"Erreur lors de la récupération du patient: {str(e)}")

    @staticmethod
    def get_patients_by_acronyme(acronyme: str, exclude_id: int = None):
        with SessionLocal() as db:
            try:
                query = db.query(Patient).filter(Patient.acronyme == acronyme)
                if exclude_id is not None:
                    query = query.filter(Patient.id != exclude_id)
                return query.all()
            except SQLAlchemyError as e:
                raise DatabaseException(f"Erreur lors de la recherche par acronyme: {str(e)}")

    @staticmethod
    def add_patient(patient: Patient) -> int:
        with SessionLocal() as db:
            try:
                patient.id = None  # Force la base de données à générer un nouvel ID
                db.add(patient)
                db.commit()
                db.refresh(patient)
                return patient.id
            except SQLAlchemyError as e:
                db.rollback()
                raise DatabaseException(f"Erreur lors de l'ajout du patient : {str(e)}")

    @staticmethod
    def update_patient(patient_id: int, updated_data: Patient):
        with SessionLocal() as db:
            try:
                patient = db.get(Patient, int(patient_id))
                if patient:
                    # Mise à jour de toutes les propriétés
                    patient.nom = updated_data.nom
                    patient.prenom = updated_data.prenom
                    patient.sexe = updated_data.sexe
                    patient.date_naissance = updated_data.date_naissance
                    patient.adresse = updated_data.adresse
                    patient.amenagement = updated_data.amenagement
                    patient.niveau = updated_data.niveau
                    patient.ecole = updated_data.ecole
                    patient.ville = updated_data.ville
                    patient.telephone1 = updated_data.telephone1
                    patient.typeTelephone1 = updated_data.typeTelephone1
                    patient.telephone2 = updated_data.telephone2
                    patient.typeTelephone2 = updated_data.typeTelephone2
                    patient.email = updated_data.email
                    patient.etat_suivi = updated_data.etat_suivi
                    patient.description = updated_data.description
                    patient.nom_facturation = updated_data.nom_facturation
                    patient.acronyme = updated_data.acronyme
                    
                    db.commit()
            except SQLAlchemyError as e:
                db.rollback()
                raise DatabaseException(f"Erreur lors de la mise à jour du patient : {str(e)}")

    @staticmethod
    def delete_patient(patient_id: int):
        with SessionLocal() as db:
            try:
                patient = db.get(Patient, int(patient_id))
                if patient:
                    db.delete(patient)
                    db.commit()
            except SQLAlchemyError as e:
                db.rollback()
                raise DatabaseException(f"Erreur lors de la suppression du patient : {str(e)}")
