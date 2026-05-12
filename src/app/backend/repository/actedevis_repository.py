from app.backend.database.database import SessionLocal
from app.backend.model.acte_devis import ActeDevis
from app.exceptions import DatabaseException
from sqlalchemy.exc import SQLAlchemyError

class ActeDevisRepository:
    def __init__(self):
        pass
    
    @staticmethod
    def add_acte(acte: ActeDevis) -> tuple[str, int]:
        with SessionLocal() as db:
            try:
                db.add(acte)
                db.commit()
                db.refresh(acte)
                return acte.id_devis, acte.id_type_rdv
            except SQLAlchemyError as e:
                db.rollback()
                raise DatabaseException(f"Erreur lors de l'ajout de l'acte : {str(e)}")

    @staticmethod
    def get_acte_by_id(devis_id: str, type_rdv_id: int) -> ActeDevis | None:
        with SessionLocal() as db:
            try:
                return db.query(ActeDevis).filter(ActeDevis.id_devis == devis_id, ActeDevis.id_type_rdv == type_rdv_id).first()
            except SQLAlchemyError as e:
                raise DatabaseException(f"Erreur lors de la récupération de l'acte : {str(e)}")

    @staticmethod
    def get_all_actes() -> list[ActeDevis]:
        with SessionLocal() as db:
            try:
                return db.query(ActeDevis).all()
            except SQLAlchemyError as e:
                raise DatabaseException(f"Erreur lors de la récupération des actes : {str(e)}")

    @staticmethod
    def delete_acte(devis_id: str, type_rdv_id: int) -> None:
        with SessionLocal() as db:
            try:
                acte = db.query(ActeDevis).filter(ActeDevis.id_devis == devis_id, ActeDevis.id_type_rdv == type_rdv_id).first()
                if acte:
                    db.delete(acte)
                    db.commit()
            except SQLAlchemyError as e:
                db.rollback()
                raise DatabaseException(f"Erreur lors de la suppression de l'acte : {str(e)}")
            
    @staticmethod
    def get_actes_by_devis_id(devis_id: str) -> list[ActeDevis]:
        with SessionLocal() as db:
            try:
                return db.query(ActeDevis).filter(ActeDevis.id_devis == devis_id).all()
            except SQLAlchemyError as e:
                raise DatabaseException(f"Erreur lors de la récupération des actes pour le devis {devis_id} : {str(e)}")