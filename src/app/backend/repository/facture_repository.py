from datetime import datetime, date
from app.backend.database import database
from app.backend.model.facture import Facture
from app.exceptions import DatabaseException
from sqlalchemy import desc
from sqlalchemy.exc import SQLAlchemyError

class FactureRepository:
    def __init__(self):
        pass
    
    @staticmethod
    def add_facture(facture: Facture) -> str:
        with database.SessionLocal() as db:
            try:
                if facture.date_emission is None:
                    facture.date_emission = datetime.today().date()
                if facture.statut is None:
                    facture.statut = "IMPAYE"
                
                db.add(facture)
                db.commit()
                db.refresh(facture)
                return facture.id
            except SQLAlchemyError as e:
                db.rollback()
                raise DatabaseException(f"Erreur lors de l'ajout de la facture : {str(e)}")

    @staticmethod
    def get_facture_by_id(facture_id: str) -> Facture | None:
        with database.SessionLocal() as db:
            try:
                return db.query(Facture).filter(Facture.id == facture_id).first()
            except SQLAlchemyError as e:
                raise DatabaseException(f"Erreur lors de la récupération de la facture : {str(e)}")

    @staticmethod
    def get_all_factures() -> list[Facture]:
        with database.SessionLocal() as db:
            try:
                return db.query(Facture).all()
            except SQLAlchemyError as e:
                raise DatabaseException(f"Erreur lors de la récupération des factures : {str(e)}")

    @staticmethod
    def update_facture_status(facture_id: str, new_statut: str = "IMPAYE", date_paiement: date = None) -> None:
        with database.SessionLocal() as db:
            try:
                facture = db.query(Facture).filter(Facture.id == facture_id).first()
                if facture:
                    facture.statut = new_statut
                    facture.date_paiement = date_paiement
                    db.commit()
            except SQLAlchemyError as e:
                db.rollback()
                raise DatabaseException(f"Erreur lors de la mise à jour de la facture : {str(e)}")

    @staticmethod
    def delete_facture(facture_id: str) -> None:
        with database.SessionLocal() as db:
            try:
                facture = db.query(Facture).filter(Facture.id == facture_id).first()
                if facture:
                    db.delete(facture)
                    db.commit()
            except SQLAlchemyError as e:
                db.rollback()
                raise DatabaseException(f"Erreur lors de la suppression de la facture : {str(e)}")

    @staticmethod
    def get_factures_impaye_by_patient_id(patient_id: int) -> list[Facture]:
        with database.SessionLocal() as db:
            try:
                return db.query(Facture).filter(Facture.statut == 'IMPAYE', Facture.patient_id == patient_id).all()
            except SQLAlchemyError as e:
                raise DatabaseException(f"Erreur lors de la récupération des factures impayées : {str(e)}")

    @staticmethod
    def generate_numero_facture(date_emission: date = None) -> str:
        if date_emission is None:
            date_emission = datetime.today().date()
        annee_mois = date_emission.strftime('%Y-%m')
        prefix = f"FAC-{annee_mois}-"
        
        with database.SessionLocal() as db:
            try:
                last_facture = db.query(Facture).filter(Facture.id.like(f"{prefix}%")).order_by(desc(Facture.id)).first()
                
                if last_facture:
                    num = int(last_facture.id.split('-')[-1])
                else:
                    num = 0
                    
                next_num = num + 1
                return f"{prefix}{str(next_num).zfill(3)}"
            except SQLAlchemyError as e:
                raise DatabaseException(f"Erreur lors de la génération du numéro de facture : {str(e)}")
