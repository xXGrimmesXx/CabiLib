from app.backend.database import database
from app.backend.model.ligneFacture import LigneFacture
from app.backend.model.rendezVous import RendezVous
from app.exceptions import DatabaseException
from sqlalchemy.exc import SQLAlchemyError

class LigneFactureRepository:
    """SERVICE - Contient la logique d'accès aux données pour l'entité LigneFacture"""

    @staticmethod
    def get_all_lignes():
        with database.SessionLocal() as db:
            try:
                return db.query(LigneFacture).all()
            except SQLAlchemyError as e:
                raise DatabaseException(f"Erreur lors de la récupération des lignes : {str(e)}")

    @staticmethod
    def get_ligne(id_facture: str, id_rdv: int):
        with database.SessionLocal() as db:
            try:
                return db.query(LigneFacture).filter(
                    LigneFacture.idFacture == id_facture,
                    LigneFacture.idRendezVous == int(id_rdv)
                ).first()
            except SQLAlchemyError as e:
                raise DatabaseException(f"Erreur lors de la récupération de la ligne : {str(e)}")

    @staticmethod
    def add_ligne(ligne: LigneFacture):
        with database.SessionLocal() as db:
            try:
                db.add(ligne)
                db.commit()
            except SQLAlchemyError as e:
                db.rollback()
                raise DatabaseException(f"Erreur lors de l'ajout de ligne de facture : {str(e)}")

    @staticmethod
    def delete_ligne(id_facture: str, id_rdv: int):
        with database.SessionLocal() as db:
            try:
                ligne = db.query(LigneFacture).filter(
                    LigneFacture.idFacture == id_facture,
                    LigneFacture.idRendezVous == int(id_rdv)
                ).first()
                if ligne:
                    db.delete(ligne)
                    db.commit()
            except SQLAlchemyError as e:
                db.rollback()
                raise DatabaseException(f"Erreur lors de la suppression de ligne de facture : {str(e)}")

    @staticmethod
    def get_lignes_by_facture_id(id_facture: str):
        with database.SessionLocal() as db:
            try:
                return db.query(LigneFacture).filter(LigneFacture.idFacture == id_facture).all()
            except SQLAlchemyError as e:
                raise DatabaseException(f"Erreur lors de la récupération des lignes par facture : {str(e)}")

    @staticmethod
    def get_lignes_by_patient_id(patient_id: int):
        with database.SessionLocal() as db:
            try:
                # Jointure avec rendez_vous
                lignes = db.query(LigneFacture).join(RendezVous, LigneFacture.idRendezVous == RendezVous.id).filter(RendezVous.patient_id == int(patient_id)).all()
                return lignes
            except SQLAlchemyError as e:
                raise DatabaseException(f"Erreur lors de la récupération des lignes par patient : {str(e)}")

    @staticmethod
    def get_lignes_by_rdv_id(id_rdv: int):
        with database.SessionLocal() as db:
            try:
                return db.query(LigneFacture).filter(LigneFacture.idRendezVous == int(id_rdv)).all()
            except SQLAlchemyError as e:
                raise DatabaseException(f"Erreur lors de la récupération des lignes par rdv : {str(e)}")
