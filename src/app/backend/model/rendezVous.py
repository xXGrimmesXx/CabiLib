from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from app.backend.database.database import Base
import traceback
from datetime import datetime, timedelta
from app.backend.model.typeRDV import TypeRDV
from json import dumps, loads
from app.backend.services.internet_API_thread_worker import APIRequestQueue


class RendezVous(Base):
    __tablename__ = "rendez_vous"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    patient_id = Column(Integer, ForeignKey('patient.id'))
    adresse_id = Column(Integer, ForeignKey('contact.id'), nullable=True)
    date = Column(DateTime)
    motif = Column(String)
    type_id = Column(Integer, ForeignKey('type_rdv.id'))
    presence = Column(String)
    facture_id = Column(String, ForeignKey('facture.id'))
    google_calendar_id = Column(String)

    def __repr__(self) -> str:
        """
        Retourne une représentation textuelle du rendez-vous.

        Returns:
            str: Représentation lisible du rendez-vous.
        """
        return f"RendezVous(ID: {self.id}, Patient ID: {self.patient_id}, Date: {self.date.strftime('%Y-%m-%d %H:%M:%S') if self.date else None}, Motif: {self.motif}, Type ID: {self.type_id})"
    def serialize(self) -> dict:
        """
        Sérialise l'objet RendezVous en dictionnaire.

        Returns:
            dict: Dictionnaire représentant le rendez-vous.
        """
        return dumps({
            "id": self.id,
            "patient_id": self.patient_id,
            "adresse_id": self.adresse_id,
            "date": self.date.isoformat() if isinstance(self.date, datetime) else str(self.date),
            "motif": self.motif,
            "type_id": self.type_id,
            "presence": self.presence,
            "facture_id": self.facture_id,
            "google_calendar_id": self.google_calendar_id
        })
    
    @staticmethod
    def parse(serialized_str: str) -> 'RendezVous':
        """
        Désérialise une chaîne JSON en objet RendezVous.

        Args:
            serialized_str (str): Chaîne JSON représentant le rendez-vous.

        Returns:
            RendezVous: Instance de RendezVous.
        """
        data = loads(serialized_str)
        date_parsed = datetime.fromisoformat(data["date"]) if "T" in data["date"] else datetime.strptime(data["date"], '%Y-%m-%d %H:%M:%S')
        return RendezVous(
            id=data.get("id"),
            patient_id=data["patient_id"],
            date=date_parsed,
            motif=data["motif"],
            type_id=data["type_id"],
            presence=data["presence"],
            facture_id=data.get("facture_id", "-1"),
            google_calendar_id=data.get("google_calendar_id", ""),
            adresse_id=data.get("adresse_id", None)
        )
    