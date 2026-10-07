from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from app.backend.database.database import Base
import traceback
from datetime import datetime, timedelta
from app.backend.model.typeRDV import TypeRDV
from json import dumps, loads
from app.backend.services.internet_API_thread_worker import APIRequestQueue


class Note(Base):
    __tablename__ = "note"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    date = Column(DateTime)
    titre = Column(String)
    description = Column(String)
    couleur = Column(String)
    google_calendar_id = Column(String)
    duree_minutes = Column("duree", Integer)  # Durée en minutes


    @property
    def duree(self):
        return timedelta(minutes=self.duree_minutes) if self.duree_minutes is not None else timedelta()

    @duree.setter
    def duree(self, value):
        if isinstance(value, timedelta):
            self.duree_minutes = int(value.total_seconds() // 60)
        else:
            self.duree_minutes = int(value)

    def __repr__(self) -> str:
        """
        Retourne une représentation textuelle de la note.

        Returns:
            str: Représentation lisible de la note.
        """
        return f"Note(ID: {self.id}, Titre: {self.titre}, Date: {self.date.strftime('%Y-%m-%d %H:%M:%S') if self.date else None})"

    def serialize(self) -> dict:
        """
        Sérialise l'objet Note en dictionnaire.

        Returns:
            dict: Dictionnaire représentant la note.
        """
        return dumps({
            "id": self.id,
            "titre": self.titre,
            "description": self.description,
            "couleur": self.couleur,
            "date": self.date.isoformat() if isinstance(self.date, datetime) else str(self.date),
            "google_calendar_id": self.google_calendar_id,
            "duree_minutes": self.duree_minutes
        })
    
    @staticmethod
    def parse(serialized_str: str) -> 'Note':
        """
        Désérialise une chaîne JSON en objet Note.

        Args:
            serialized_str (str): Chaîne JSON représentant la note.

        Returns:
            Note: Instance de Note.
        """
        data = loads(serialized_str)
        date_parsed = datetime.fromisoformat(data["date"]) if "T" in data["date"] else datetime.strptime(data["date"], '%Y-%m-%d %H:%M:%S')
        return Note(
            id=data.get("id"),
            titre=data["titre"],
            description=data["description"],
            couleur=data["couleur"],
            date=date_parsed,
            duree_minutes=data.get("duree_minutes"),
            google_calendar_id=data.get("google_calendar_id", "")
        )