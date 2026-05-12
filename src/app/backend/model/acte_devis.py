from sqlalchemy import Column, String, Integer, Date, ForeignKey
from app.backend.database.database import Base
from datetime import datetime

class ActeDevis(Base):
    __tablename__ = "acte_devis"

    id_devis = Column(String, ForeignKey('devis.id'), primary_key=True)
    id_type_rdv = Column(Integer, ForeignKey('type_rdv.id'), primary_key=True)
    quantite = Column(Integer, default=0)

    def __repr__(self) -> str:
        """
        Retourne une représentation textuelle de l'acte du devis.

        Returns:
            str: Représentation lisible de l'acte du devis.
        """
        return f"ActeDevis(ID: {self.id_devis}, Type RDV ID: {self.id_type_rdv}, Quantité: {self.quantite})"