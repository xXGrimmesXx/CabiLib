from datetime import datetime
from dateutil import relativedelta
from app.backend.model.note import Note
from app.backend.repository.note_repository import NoteRepository
from app.backend.model.rendezVous import RendezVous
from app.exceptions import RegleMetierException, ConflitHoraireException

class NoteService:

    @staticmethod
    def get_all_notes():
        return NoteRepository.get_all_notes()

    @staticmethod
    def get_note_by_id(note_id: int):
        return NoteRepository.get_note_by_id(note_id)

    
    @staticmethod
    def get_notes_by_plage(date_debut: datetime, date_fin: datetime):
        return NoteRepository.get_notes_by_plage(date_debut, date_fin)

    @staticmethod
    def get_notes_by_datetime(exact_date: datetime):
        return NoteRepository.get_notes_by_datetime(exact_date)

    @staticmethod
    def add_note(note: Note):
        # REGLES METIER
        if not note.date or not note.duree_minutes:
            raise RegleMetierException("La note doit obligatoirement avoir une date et une durée.")
        if note.duree_minutes <= 0:
            raise RegleMetierException("La durée de la note doit être supérieure à 0 minutes.")
        if not note.titre:
            raise RegleMetierException("La note doit obligatoirement avoir un titre.")
        if not NoteRepository.creneau_libre(note):
            raise ConflitHoraireException("Conflit d'horaire : Le créneau horaire est déjà occupé.")

        return NoteRepository.add_note(note)

    @staticmethod
    def update_note(note_id: int, new_note: Note):
        if not new_note.date or not new_note.duree_minutes:
            raise RegleMetierException("La note doit obligatoirement avoir une date et une durée.")
        if new_note.duree_minutes <= 0:
            raise RegleMetierException("La durée de la note doit être supérieure à 0 minutes.")
        if not new_note.titre:
            raise RegleMetierException("La note doit obligatoirement avoir un titre.")
            
        if not NoteRepository.creneau_libre(new_note):
            raise ConflitHoraireException("Conflit d'horaire : Le créneau horaire est déjà occupé.")
            
        return NoteRepository.update_note(note_id, new_note)

    @staticmethod
    def delete_note(note_id: int):
        return NoteRepository.delete_note(note_id)