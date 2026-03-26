from app.backend.database.database import SessionLocal
from app.backend.model.typeRDV import TypeRDV
from app.backend.model.rendezVous import RendezVous
from app.backend.services.internet_API_thread_worker import APIRequestQueue
from app.exceptions import DatabaseException, GoogleCalendarException
from sqlalchemy.exc import SQLAlchemyError
import traceback

class TypeRDVRepository:
    """SERVICE - Contient la logique d'accès aux données pour l'entité TypeRDV"""

    @staticmethod
    def get_all_types():
        with SessionLocal() as db:
            try:
                return db.query(TypeRDV).all()
            except SQLAlchemyError as e:
                raise DatabaseException(f"Erreur lors de la récupération des types de rdv : {str(e)}")

    @staticmethod
    def get_type_by_id(type_id: int):
        with SessionLocal() as db:
            try:
                return db.get(TypeRDV, int(type_id))
            except SQLAlchemyError as e:
                raise DatabaseException(f"Erreur lors de la récupération du type de rdv : {str(e)}")

    @staticmethod
    def add_type(type_rdv: TypeRDV):
        with SessionLocal() as db:
            try:
                db.add(type_rdv)
                db.commit()
                db.refresh(type_rdv)
                return type_rdv
            except SQLAlchemyError as e:
                db.rollback()
                raise DatabaseException(f"Erreur lors de l'ajout du Type de RDV : {str(e)}")

    @staticmethod
    def update_type(updated_data: TypeRDV):
        with SessionLocal() as db:
            try:
                type_rdv = db.get(TypeRDV, int(updated_data.id))
                if type_rdv:
                    # Vérifications pour l'API calendrier
                    needs_calendar_update = False
                    if type_rdv.duree_minutes != updated_data.duree_minutes or type_rdv.nom != updated_data.nom:
                        needs_calendar_update = True

                    type_rdv.nom = updated_data.nom
                    type_rdv.description = updated_data.description
                    type_rdv.prix = updated_data.prix
                    type_rdv.duree_minutes = updated_data.duree_minutes
                    type_rdv.localisation = updated_data.localisation
                    type_rdv.couleur = updated_data.couleur
                    type_rdv.estgroupe = updated_data.estgroupe
                    
                    db.commit()

                    if needs_calendar_update:
                        # Plus propre à l'avenir de passer par rdv_service
                        rendezvous_list = db.query(RendezVous).filter(RendezVous.type_id == updated_data.id).all()
                        for rdv in rendezvous_list:
                            try:
                                APIRequestQueue.enqueue_api_request('calendar_modify_rdv', rdv.serialize())
                            except Exception as e:
                                print(f"[ERREUR CALENDAR] {e}")
                                traceback.print_exc()
            except SQLAlchemyError as e:
                db.rollback()
                raise DatabaseException(f"Erreur lors de la mise à jour du Type de RDV : {str(e)}")

    @staticmethod
    def delete_type(type_rdv_id: int):
        with SessionLocal() as db:
            try:
                type_rdv = db.get(TypeRDV, int(type_rdv_id))
                if type_rdv:
                    db.delete(type_rdv)
                    db.commit()
            except SQLAlchemyError as e:
                db.rollback()
                raise DatabaseException(f"Erreur lors de la suppression du Type de RDV : {str(e)}")

    @staticmethod
    def has_linked_rendezvous(type_rdv_id: int) -> bool:
        with SessionLocal() as db:
            try:
                return db.query(RendezVous).filter(RendezVous.type_id == int(type_rdv_id)).count() > 0
            except SQLAlchemyError as e:
                raise DatabaseException(f"Erreur DB : {str(e)}")
