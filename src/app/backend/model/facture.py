from sqlalchemy import Boolean, Column, String, Integer, Date, ForeignKey
from app.backend.database.database import Base
from datetime import datetime

class Facture(Base):
    __tablename__ = "facture"

    id = Column(String, primary_key=True)
    patient_id = Column(Integer, ForeignKey('patient.id'))
    date_emission = Column(Date, default=datetime.today().date)
    description = Column(String)
    statut = Column(String, default="IMPAYE")
    date_paiement = Column(Date, nullable=True)
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    regle = Column(Boolean, default=False)  # Nouveau champ pour indiquer si la facture est réglée
    methode_paiement = Column(String, nullable=True)  # Nouveau champ pour la méthode de paiement


    def __repr__(self) -> str:
        """
        Retourne une représentation textuelle de la facture.

        Returns:
            str: Représentation lisible de la facture.
        """
        return f"Facture(ID: {self.id}, Patient ID: {self.patient_id}, Date d'émission: {self.date_emission}, Description: {self.description}, Statut: {self.statut}, Date de paiement: {self.date_paiement}, Date de début: {self.start_date}, Date de fin: {self.end_date}, Réglée: {self.regle}, Méthode de paiement: {self.methode_paiement})"