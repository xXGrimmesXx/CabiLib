from sqlalchemy import Column, Integer, String, Float, Boolean
from app.backend.database.database import Base
from datetime import timedelta

class TypeRDV(Base):
    __tablename__ = "type_rdv"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nom = Column(String)
    description = Column(String)
    prix = Column(Float)
    duree_minutes = Column('duree', Integer)  # Le nom dans la db est duree
    localisation = Column(String)
    couleur = Column(String)
    estgroupe = Column(Boolean)

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
        return f"TypeRDV(ID: {self.id}, Nom: {self.nom}, Description: {self.description}, Prix: {self.prix})"