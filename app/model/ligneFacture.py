from database.setup_db import DB_PATH
import sqlite3


class LigneFacture:
    def __init__(self,facture_id, rdv_id,montant_facture):
        self.facture_id = facture_id
        self.rdv_id = rdv_id
        self.montant_facture = montant_facture

    def __repr__(self):
        return f"LigneFacture(Facture ID: {self.facture_id}, Rendez-vous ID: {self.rdv_id})"
    
    @staticmethod
    def getAllLignesFacture():
        connexion = sqlite3.connect(DB_PATH)
        cursor = connexion.cursor()

        cursor.execute("SELECT * FROM ligne_facture")
        lignes_data = cursor.fetchall()
        connexion.close()

        lignes = []
        for data in lignes_data:
            ligne = LigneFacture(
                facture_id=data[1],
                rdv_id=data[0],
                montant_facture=data[2]
            )
            lignes.append(ligne)
        
        return lignes
    
    @staticmethod
    def getLigneFacture(idFacture, idRendezVous):
        connexion = sqlite3.connect(DB_PATH)
        cursor = connexion.cursor()

        cursor.execute("SELECT * FROM ligne_facture WHERE idFacture = ? AND idRendezVous = ?", (idFacture, idRendezVous))
        data = cursor.fetchone()
        connexion.close()

        if data:
            return LigneFacture(
                facture_id=data[1],
                rdv_id=data[0],
                montant_facture=data[2]
            )
        return None
    
    @staticmethod
    def addLigneFacture(ligne_facture):
        connexion = sqlite3.connect(DB_PATH)
        cursor = connexion.cursor()

        cursor.execute(
            "INSERT INTO ligne_facture (idRendezVous, idFacture, montant_facture) VALUES (?, ?, ?)",
            (ligne_facture.rdv_id, ligne_facture.facture_id, ligne_facture.montant_facture)
        )
        connexion.commit()
        connexion.close()
    
    @staticmethod
    def deleteLigneFacture(idFacture, idRendezVous):
        connexion = sqlite3.connect(DB_PATH)
        cursor = connexion.cursor()

        cursor.execute(
            "DELETE FROM ligne_facture WHERE idFacture = ? AND idRendezVous = ?",
            (idFacture, idRendezVous)
        )
        connexion.commit()
        connexion.close()

    @staticmethod
    def getAllLignesByFactureId(facture_id):
        connexion = sqlite3.connect(DB_PATH)
        cursor = connexion.cursor()

        cursor.execute("SELECT * FROM ligne_facture WHERE idFacture = ?", (facture_id,))
        lignes_data = cursor.fetchall()
        connexion.close()

        lignes = []
        for data in lignes_data:
            ligne = LigneFacture(
                facture_id=data[1],
                rdv_id=data[0],
                montant_facture=data[2]
            )
            lignes.append(ligne)
        
        return lignes
    
    @staticmethod
    def getAllLignesByPatientId(patient_id):
        connexion = sqlite3.connect(DB_PATH)
        cursor = connexion.cursor()


        cursor.execute("SELECT lf FROM lignes_facture lf, rendez_vous rv WHERE lf.idRendezVous = rv.id AND rv.patient_id = ?", (patient_id,))
        lignes_data = cursor.fetchall()
        connexion.close()

        lignes = []
        for data in lignes_data:
            ligne = LigneFacture(
                rdv_id=data[0],
                facture_id=data[1],
                montant_facture=data[2]
            )
            lignes.append(ligne)
        
        return lignes