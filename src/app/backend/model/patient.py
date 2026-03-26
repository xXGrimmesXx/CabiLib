from sqlalchemy import Column, Integer, String, Date, Text
from app.backend.database.database import Base
from datetime import datetime

class Patient(Base):
    __tablename__ = "patient"

    # Colonnes SQLAlchemy
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nom = Column(String)
    prenom = Column(String)
    sexe = Column(String)
    date_naissance = Column(Date)
    adresse = Column(String)
    amenagement = Column(String)
    niveau = Column(String)
    ecole = Column(String)
    ville = Column(String)
    telephone1 = Column(String)
    typeTelephone1 = Column(String)
    telephone2 = Column(String)
    typeTelephone2 = Column(String)
    email = Column(String)
    etat_suivi = Column(String)
    description = Column(Text)
    nom_facturation = Column(String)
    acronyme = Column(String, unique=True)

    def __repr__(self) -> str:
        """
        Retourne une représentation textuelle du patient.

        Returns:
            str: Représentation lisible du patient.
        """
        return f"Patient({self.nom} {self.prenom}, {self.sexe})"

    def adresse_complete(self) -> str:
        """
        Retourne l'adresse complète du patient.

        Returns:
            str: Adresse complète.
        """
        if self.adresse is None and self.ville is None :
            return ""
        
        elif self.adresse is None :
            return self.ville
        
        elif self.ville is None :
            return self.adresse
        return f"{self.adresse}, {self.ville}"