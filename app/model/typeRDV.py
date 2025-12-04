from database.setup_db import DB_PATH
import sqlite3
from datetime import timedelta

class TypeRDV:
    def __init__(self, id, nom, description, prix, duree, localisation, couleur, estgroupe):
        self.id = id
        self.nom = nom
        self.description = description
        self.prix = prix
        self.duree = duree
        self.localisation = localisation
        self.couleur = couleur
        self.estgroupe = estgroupe

    def __repr__(self):
        return f"TypeRDV(ID: {self.id}, Nom: {self.nom}, Description: {self.description}, Prix: {self.prix})"
    
    @staticmethod
    def getAllTypesRDV():
        connexion = sqlite3.connect(DB_PATH)
        cursor = connexion.cursor()

        cursor.execute("SELECT * FROM type_rdv")
        types_data = cursor.fetchall()
        connexion.close()

        types = []
        for data in types_data:
            h,m=map(int, data[4].split(':'))
            type_rdv = TypeRDV(
                id=data[0],
                nom=data[1],
                description=data[2],
                prix=data[3],
                duree=timedelta(hours=h, minutes=m, seconds=0),
                localisation=data[5],
                couleur=data[6],
                estgroupe=data[7]
            )
            types.append(type_rdv)
        
        return types
    
    @staticmethod
    def getTypeRDVById(type_id):
        connexion = sqlite3.connect(DB_PATH)
        cursor = connexion.cursor()

        cursor.execute("SELECT * FROM type_rdv WHERE id = ?", (type_id,))
        data = cursor.fetchone()
        connexion.close()

        if data:
            h,m=map(int, data[4].split(':'))
            return TypeRDV(
                id=data[0],
                nom=data[1],
                description=data[2],
                prix=data[3],
                duree=timedelta(hours=h, minutes=m, seconds=0),
                localisation=data[5],
                couleur=data[6],
                estgroupe=data[7]
            )
        return None
    
    @staticmethod
    def addTypeRDV(typeRDV):
        connexion = sqlite3.connect(DB_PATH)
        cursor = connexion.cursor()

        cursor.execute(
            "INSERT INTO type_rdv (nom, description, prix, duree, localisation, couleur,estgroupe) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (typeRDV.nom, typeRDV.description, typeRDV.prix, str(typeRDV.duree), typeRDV.localisation, typeRDV.couleur,typeRDV.estgroupe)
        )
        connexion.commit()
        connexion.close()
    
    @staticmethod
    def updateTypeRDV(type_rdv):
        """Mettre à jour un type de RDV"""
        connexion = sqlite3.connect(DB_PATH)
        cursor = connexion.cursor()
        cursor.execute("""
            UPDATE type_rdv 
            SET nom = ?, description = ?, prix = ?, duree = ?, localisation = ?, couleur = ?, estgroupe = ?
            WHERE id = ?
        """, (type_rdv.nom, type_rdv.description, type_rdv.prix, str(type_rdv.duree), type_rdv.localisation, type_rdv.couleur, type_rdv.estgroupe, type_rdv.id))
        connexion.commit()
        connexion.close()
    
    @staticmethod
    def deleteTypeRDV(type_rdv_id):
        """Supprimer un type de RDV"""
        connexion = sqlite3.connect(DB_PATH)
        cursor = connexion.cursor()
        cursor.execute("DELETE FROM type_rdv WHERE id = ?", (type_rdv_id,))
        connexion.commit()
        connexion.close()