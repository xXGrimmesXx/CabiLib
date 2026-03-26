from sqlalchemy import Column, Integer, String, Float, ForeignKey
from app.backend.database.database import Base

class LigneFacture(Base):
    __tablename__ = "ligne_facture"

    idRendezVous = Column(Integer, ForeignKey('rendez_vous.id'), primary_key=True)
    idFacture = Column(String, ForeignKey('facture.id'), primary_key=True)
    montant_facture = Column(Float)

    def __repr__(self) -> str:
        return f"LigneFacture(Facture ID: {self.idFacture}, Rendez-vous ID: {self.idRendezVous}, Montant: {self.montant_facture})"