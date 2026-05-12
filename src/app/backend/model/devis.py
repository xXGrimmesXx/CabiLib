from sqlalchemy import Column, String, Integer, Date, ForeignKey
from app.backend.database.database import Base
from datetime import datetime

class Devis(Base):
    __tablename__ = "devis"

    id = Column(String, primary_key=True)
    patient_id = Column(Integer, ForeignKey('patient.id'))
    date_emission = Column(Date, default=datetime.today().date)
    date_debut = Column(Date, nullable=True)
    date_fin = Column(Date, nullable=True)

    def __repr__(self) -> str:
        """
        Retourne une représentation textuelle du devis.

        Returns:
            str: Représentation lisible du devis.
        """
        return f"Devis(ID: {self.id}, Patient ID: {self.patient_id}, Date d'émission: {self.date_emission}, Date de début: {self.date_debut}, Date de fin: {self.date_fin})"