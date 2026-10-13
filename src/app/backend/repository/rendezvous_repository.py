from typing import List

from sqlalchemy import or_, and_, func
from app.backend.database import database
from app.backend.model.note import Note
from app.backend.model.rendezVous import RendezVous
from app.backend.model.typeRDV import TypeRDV
from app.backend.services.internet_API_thread_worker import APIRequestQueue
from app.exceptions import DatabaseException
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime, timedelta
import traceback

class RendezVousRepository:
    """SERVICE - Contient la logique d'accès aux données pour l'entité RendezVous"""

    @staticmethod
    def get_all_rendezvous():
        with database.SessionLocal() as db:
            try:
                return db.query(RendezVous).all()
            except SQLAlchemyError as e:
                raise DatabaseException(f"Erreur lors de la récupération des rendez-vous : {str(e)}")

    @staticmethod
    def get_rendezvous_by_id(rdv_id: int):
        with database.SessionLocal() as db:
            try:
                return db.get(RendezVous, int(rdv_id))
            except SQLAlchemyError as e:
                raise DatabaseException(f"Erreur lors de la récupération du rendez-vous : {str(e)}")

    @staticmethod
    def get_rendezvous_by_patient_id(patient_id: int):
        with database.SessionLocal() as db:
            try:
                return db.query(RendezVous).filter(RendezVous.patient_id == int(patient_id)).all()
            except SQLAlchemyError as e:
                raise DatabaseException(f"Erreur lors de la récupération des rdvs par patient : {str(e)}")

    @staticmethod
    def get_rendezvous_by_plage(date_debut: datetime, date_fin: datetime):
        with database.SessionLocal() as db:
            try:
                return db.query(RendezVous).filter(
                    RendezVous.date >= date_debut,
                    RendezVous.date <= date_fin
                ).all()
            except SQLAlchemyError as e:
                raise DatabaseException(f"Erreur lors de la récupération par plage : {str(e)}")

    @staticmethod
    def get_rendezvous_by_datetime(exact_date: datetime):
        with database.SessionLocal() as db:
            try:
                # Créer une plage d'une seconde pour éviter les problèmes de comparaison stricte avec les dates sous SQLite
                start = exact_date.replace(microsecond=0)-timedelta(seconds=1)
                end = start + timedelta(seconds=1)
                return db.query(RendezVous).filter(RendezVous.date >= start,RendezVous.date <= end).all()
            except SQLAlchemyError as e:
                raise DatabaseException(f"Erreur lors de la récupération du rendez-vous à la date exacte : {str(e)}")

    @staticmethod
    def get_rendezvous_by_patient_and_date_range(patient_id: int, start_date: datetime, end_date: datetime):
        with database.SessionLocal() as db:
            try:
                return db.query(RendezVous).filter(
                    RendezVous.patient_id == int(patient_id),
                    RendezVous.date >= start_date,
                    RendezVous.date <= end_date
                ).all()
            except SQLAlchemyError as e:
                raise DatabaseException(f"Erreur DB : {str(e)}")

    @staticmethod
    def get_rendezvous_by_facture_id(facture_id: str):
        with database.SessionLocal() as db:
            try:
                return db.query(RendezVous).filter(RendezVous.facture_id == facture_id).all()
            except SQLAlchemyError as e:
                raise DatabaseException(f"Erreur DB : {str(e)}")

    @staticmethod
    def creneau_libre(rendezvous: RendezVous) -> bool:
        from app.backend.repository.note_repository import NoteRepository
        with database.SessionLocal() as db:
            type_rdv = db.get(TypeRDV, int(rendezvous.type_id))
            if not type_rdv:
                print(f"[ERREUR] TypeRDV introuvable pour le rendez-vous ID {rendezvous.id} avec type_id {rendezvous.type_id}")
                return False
            

            duree_minutes = type_rdv.duree_minutes
            dureetime = timedelta(minutes=duree_minutes)
            date_debut = rendezvous.date
            date_fin = rendezvous.date + dureetime

            # Requête pour trouver des créneaux qui se chevauchent
            jour_debut = date_debut.replace(hour=0, minute=0, second=0, microsecond=0)
            jour_fin = date_fin.replace(hour=23, minute=59, second=59, microsecond=999999)
            all_rdvs = RendezVousRepository.get_rendezvous_by_plage(jour_debut, jour_fin)
            all_notes = NoteRepository.get_notes_by_plage(date_debut, date_fin)
            overlapping_rdvs :List[tuple[RendezVous, TypeRDV]] = []
            overlapping_notes :List[Note] = []

            for r in all_rdvs:
                if not r:
                    continue
                r_type = db.get(TypeRDV, int(r.type_id))
                if not r_type:
                    continue
                
                r_debut = r.date
                r_fin = r.date + timedelta(minutes=r_type.duree_minutes)

                if (r_debut <= date_debut and r_fin > date_debut) or \
                   (r_debut >= date_debut and r_fin <= date_fin) or \
                   (r_debut < date_fin and r_fin > date_fin) or \
                   (r_debut <= date_debut and r_fin >= date_fin):
                    overlapping_rdvs.append((r, r_type))

            for n in all_notes:
                n_debut = n.date
                n_fin = n.date + timedelta(minutes=n.duree_minutes)

                if (n_debut <= date_debut and n_fin > date_debut) or \
                    (n_debut >= date_debut and n_fin <= date_fin) or \
                    (n_debut < date_fin and n_fin > date_fin) or \
                    (n_debut <= date_debut and n_fin >= date_fin):
                    overlapping_notes.append(n)

            if len(overlapping_notes) == 0 and (len(overlapping_rdvs) == 0 or ((len(overlapping_rdvs) == 1 and overlapping_rdvs[0][0].id == rendezvous.id))):
                print("Overlapping notes")
                print(overlapping_notes)
                print("Overlapping rdvs")
                print(overlapping_rdvs)
                return True

            if type_rdv.estgroupe:
                for r, r_type in overlapping_rdvs:
                    if r.type_id != rendezvous.type_id:
                        print("Overlapping notes")
                        print(overlapping_notes)
                        print("Overlapping rdvs")
                        print(overlapping_rdvs)
                        return False
                return True
            print("Overlapping notes")
            print(overlapping_notes)
            print("Overlapping rdvs")
            print(overlapping_rdvs)
            return False

    @staticmethod
    def add_rendezvous(rdv: RendezVous):
        with database.SessionLocal() as db:
            try:
                db.add(rdv)
                db.commit()
                db.refresh(rdv)

                try:
                    APIRequestQueue.enqueue_api_request('calendar_create_event', rdv.serialize())
                except Exception as e:
                    print(f"[ERREUR CALENDAR] {e}")
                    traceback.print_exc()

                return rdv.id
            except SQLAlchemyError as e:
                db.rollback()
                raise DatabaseException(f"Erreur lors de l'ajout du rdv : {str(e)}")

    @staticmethod
    def update_rendezvous(rdv_id: int, new_rdv: RendezVous):
        with database.SessionLocal() as db:
            try:
                rdv = db.get(RendezVous, int(rdv_id))
                if rdv:
                    needs_calendar_update = False
                    if (rdv.patient_id != new_rdv.patient_id) or \
                       (rdv.date != new_rdv.date) or \
                       (rdv.motif != new_rdv.motif) or \
                       (rdv.type_id != new_rdv.type_id):
                        needs_calendar_update = True

                    rdv.patient_id = new_rdv.patient_id
                    rdv.date = new_rdv.date
                    rdv.motif = new_rdv.motif
                    rdv.type_id = new_rdv.type_id
                    rdv.presence = new_rdv.presence
                    rdv.facture_id = new_rdv.facture_id
                    rdv.google_calendar_id = new_rdv.google_calendar_id

                    db.commit()
                    db.refresh(rdv)

                    if needs_calendar_update:
                        try:
                            APIRequestQueue.enqueue_api_request('calendar_modify_rdv', rdv.serialize())
                        except Exception as e:
                            print(f"[ERREUR CALENDAR] {e}")
                            traceback.print_exc()
            except SQLAlchemyError as e:
                db.rollback()
                raise DatabaseException(f"Erreur de mise à jour du RDV : {str(e)}")

    @staticmethod
    def delete_rendezvous(rdv_id: int):
        with database.SessionLocal() as db:
            try:
                rdv = db.get(RendezVous, int(rdv_id))
                if rdv:
                    db.delete(rdv)
                    db.commit()
            except SQLAlchemyError as e:
                db.rollback()
                raise DatabaseException(f"Erreur lors de la suppression du RDV : {str(e)}")
            
    @staticmethod
    def get_montant_mois(date: datetime):
        with database.SessionLocal() as db:
            try:
                return db.query(func.sum(TypeRDV.prix)).join(RendezVous, RendezVous.type_id == TypeRDV.id).filter(
                    func.strftime('%Y-%m', RendezVous.date) == date.strftime('%Y-%m')
                ).scalar()
            except SQLAlchemyError as e:
                raise DatabaseException(f"Erreur lors du calcul du montant du mois : {str(e)}")
            
    @staticmethod
    def get_by_patient_id_and_date_range_and_type_id(patient_id: int, date_debut: datetime, date_fin: datetime, type_id: int):
        with database.SessionLocal() as db:
            try:
                return db.query(RendezVous).filter(
                    RendezVous.patient_id == int(patient_id),
                    RendezVous.date >= date_debut,
                    RendezVous.date <= date_fin,
                    RendezVous.type_id == int(type_id)
                ).all()
            except SQLAlchemyError as e:
                raise DatabaseException(f"Erreur DB : {str(e)}")
