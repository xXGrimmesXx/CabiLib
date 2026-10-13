from sqlalchemy import Column, String, Integer, ForeignKey
from app.backend.database.database import Base

class Contact(Base):
    __tablename__ = "contact"

    id = Column(String, primary_key=True)
    nom_contact = Column(String)
    patient_id = Column(Integer, ForeignKey('patient.id'))
    mail = Column(String)
    telephone = Column(String)

    def __repr__(self) -> str:
        """
        Retourne une représentation textuelle du contact.

        Returns:
            str: Représentation lisible du contact.
        """
        return f"Contact(ID: {self.id}, Nom: {self.nom_contact}, Patient ID: {self.patient_id}, Mail: {self.mail}, Téléphone: {self.telephone})"