from datetime import datetime, date
from app.backend.database import database
from app.backend.model.devis import Devis
from app.exceptions import DatabaseException
from sqlalchemy import desc
from sqlalchemy.exc import SQLAlchemyError

class DevisRepository:
    def __init__(self):
        pass
    
    @staticmethod
    def add_devis(devis: Devis) -> str:
        with database.SessionLocal() as db:
            try:
                if devis.date_emission is None:
                    devis.date_emission = datetime.today().date()
                
                db.add(devis)
                db.commit()
                db.refresh(devis)
                return devis.id
            except SQLAlchemyError as e:
                db.rollback()
                raise DatabaseException(f"Erreur lors de l'ajout du devis : {str(e)}")

    @staticmethod
    def get_devis_by_id(devis_id: str) -> Devis | None:
        with database.SessionLocal() as db:
            try:
                return db.query(Devis).filter(Devis.id == devis_id).first()
            except SQLAlchemyError as e:
                raise DatabaseException(f"Erreur lors de la récupération du devis : {str(e)}")

    @staticmethod
    def get_all_devis() -> list[Devis]:
        with database.SessionLocal() as db:
            try:
                return db.query(Devis).all()
            except SQLAlchemyError as e:
                raise DatabaseException(f"Erreur lors de la récupération des devis : {str(e)}")

    @staticmethod
    def delete_devis(devis_id: str) -> None:
        with database.SessionLocal() as db:
            try:
                devis = db.query(Devis).filter(Devis.id == devis_id).first()
                if devis:
                    db.delete(devis)
                    db.commit()
            except SQLAlchemyError as e:
                db.rollback()
                raise DatabaseException(f"Erreur lors de la suppression du devis : {str(e)}")

    @staticmethod
    def generate_numero_devis(date_emission: date = None) -> str:
        if date_emission is None:
            date_emission = datetime.today().date()
        annee_mois = date_emission.strftime('%Y-%m')
        prefix = f"DEV-{annee_mois}-"
        
        with database.SessionLocal() as db:
            try:
                last_devis = db.query(Devis).filter(Devis.id.like(f"{prefix}%")).order_by(desc(Devis.id)).first()
                
                if last_devis:
                    num = int(last_devis.id.split('-')[-1])
                else:
                    num = 0
                    
                next_num = num + 1
                return f"{prefix}{str(next_num).zfill(3)}"
            except SQLAlchemyError as e:
                raise DatabaseException(f"Erreur lors de la génération du numéro de devis : {str(e)}")
