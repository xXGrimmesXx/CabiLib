from sqlalchemy import or_, and_, func
from app.backend.database import database
from app.backend.model.note import Note
from app.backend.model.typeRDV import TypeRDV
from app.backend.services.internet_API_thread_worker import APIRequestQueue
from app.exceptions import DatabaseException
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime, timedelta

import traceback

class NoteRepository:
    """SERVICE - Contient la logique d'accès aux données pour l'entité Note"""

    @staticmethod
    def get_all_notes():
        with database.SessionLocal() as db:
            try:
                return db.query(Note).all()
            except SQLAlchemyError as e:
                raise DatabaseException(f"Erreur lors de la récupération des notes : {str(e)}")

    @staticmethod
    def get_note_by_id(note_id: int):
        with database.SessionLocal() as db:
            try:
                return db.get(Note, int(note_id))
            except SQLAlchemyError as e:
                raise DatabaseException(f"Erreur lors de la récupération de la note : {str(e)}")

    @staticmethod
    def get_notes_by_plage(date_debut: datetime, date_fin: datetime) -> list[Note]:
        with database.SessionLocal() as db:
            try:
                return db.query(Note).filter(
                    Note.date >= date_debut,
                    Note.date <= date_fin
                ).all()
            except SQLAlchemyError as e:
                raise DatabaseException(f"Erreur lors de la récupération par plage : {str(e)}")

    @staticmethod
    def get_notes_by_datetime(exact_date: datetime):
        with database.SessionLocal() as db:
            try:
                # Créer une plage d'une seconde pour éviter les problèmes de comparaison stricte avec les dates sous SQLite
                start = exact_date.replace(microsecond=0)-timedelta(seconds=1)
                end = start + timedelta(seconds=1)
                return db.query(Note).filter(Note.date >= start,Note.date <= end).all()
            except SQLAlchemyError as e:
                raise DatabaseException(f"Erreur lors de la récupération de la note à la date exacte : {str(e)}")

    @staticmethod
    def creneau_libre(note: Note) -> bool:
        from app.backend.repository.rendezvous_repository import RendezVousRepository
        with database.SessionLocal() as db:
            date_debut :datetime = note.date
            date_fin :datetime = note.date + timedelta(minutes=note.duree_minutes)

            # Requête pour trouver des créneaux qui se chevauchent
            jour_debut = date_debut.replace(hour=0, minute=0, second=0, microsecond=0)
            jour_fin = date_fin.replace(hour=23, minute=59, second=59, microsecond=999999)
            all_rdvs = RendezVousRepository.get_rendezvous_by_plage(jour_debut, jour_fin)
            all_notes = NoteRepository.get_notes_by_plage(date_debut, date_fin)
            overlapping_rdvs = []
            overlapping_notes = []

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

            if len(overlapping_rdvs) == 0 and (len(overlapping_notes) == 0 or ((len(overlapping_notes) == 1 and overlapping_notes[0].id == note.id))):
                return True

            return False

    @staticmethod
    def add_note(note: Note):
        with database.SessionLocal() as db:
            try:
                db.add(note)
                db.commit()
                db.refresh(note)

                try:
                    APIRequestQueue.enqueue_api_request('calendar_create_event', note.serialize())
                except Exception as e:
                    print(f"[ERREUR CALENDAR] {e}")
                    traceback.print_exc()

                return note.id
            except SQLAlchemyError as e:
                db.rollback()
                raise DatabaseException(f"Erreur lors de l'ajout du rdv : {str(e)}")

    @staticmethod
    def update_note(note_id: int, new_note: Note):
        with database.SessionLocal() as db:
            try:
                note = db.get(Note, int(note_id))
                if note:
                    needs_calendar_update = False
                    if (note.date != new_note.date) or \
                       (note.titre != new_note.titre) or \
                       (note.description != new_note.description) or \
                       (note.duree_minutes != new_note.duree_minutes):
                        needs_calendar_update = True

                    note.date = new_note.date
                    note.titre = new_note.titre
                    note.description = new_note.description
                    note.couleur = new_note.couleur
                    note.duree_minutes = new_note.duree_minutes
                    note.google_calendar_id = new_note.google_calendar_id

                    db.commit()
                    db.refresh(note)

                    if needs_calendar_update:
                        try:
                            APIRequestQueue.enqueue_api_request('calendar_modify_note', note.serialize())
                        except Exception as e:
                            print(f"[ERREUR CALENDAR] {e}")
                            traceback.print_exc()
            except SQLAlchemyError as e:
                db.rollback()
                raise DatabaseException(f"Erreur de mise à jour du RDV : {str(e)}")

    @staticmethod
    def delete_note(note_id: int):
        with database.SessionLocal() as db:
            try:
                note = db.get(Note, int(note_id))
                if note:
                    db.delete(note)
                    db.commit()
            except SQLAlchemyError as e:
                db.rollback()
                raise DatabaseException(f"Erreur lors de la suppression du RDV : {str(e)}")