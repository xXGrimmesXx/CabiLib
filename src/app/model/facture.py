from database.setup_db import DB_PATH
import sqlite3
import datetime

class Facture:

    def __init__(self, id, patient_id, date_emission=datetime.date.today(), description="", statut="IMPAYE", date_paiement=None):
        self.id = id
        self.patient_id = patient_id
        self.date_emission = date_emission
        self.description = description
        self.statut = statut
        self.date_paiement = date_paiement

    def __repr__(self):
        return f"Facture(ID: {self.id}, Patient ID: {self.patient_id}, Date d'émission: {self.date_emission}, Description: {self.description}, Statut: {self.statut}, Date de paiement: {self.date_paiement})"
    
    @staticmethod
    def addFacture(facture):
        connexion = sqlite3.connect(DB_PATH)
        cursor = connexion.cursor()
        # Générer le numéro de facture croissant pour le mois
        id_fac = Facture.generate_numero_facture(facture.date_emission)
        cursor.execute(
            "INSERT INTO facture (id,patient_id, date_emission, description, statut, date_paiement) VALUES (?, ?, ?, ?, ?, ?)",
            (id_fac, facture.patient_id, facture.date_emission, facture.description, facture.statut, facture.date_paiement)
        )
        connexion.commit()
        connexion.close()
        return id_fac

    @staticmethod
    def getFactureById(facture_id):
        connexion = sqlite3.connect(DB_PATH)
        cursor = connexion.cursor()

        cursor.execute("SELECT * FROM facture WHERE id = ?", (facture_id,))
        data = cursor.fetchone()
        connexion.close()

        if data:
            return Facture(
                id=data[0],
                patient_id=data[1],
                date_emission=datetime.datetime.strptime(data[2], "%Y-%m-%d").date() if data[2] else None,
                description=data[3],
                statut=data[4],
                date_paiement=datetime.datetime.strptime(data[5], "%Y-%m-%d").date() if data[5] else None
            )
        return None
    
    @staticmethod
    def getAllFactures():
        connexion = sqlite3.connect(DB_PATH)
        cursor = connexion.cursor()

        cursor.execute("SELECT * FROM facture")
        factures_data = cursor.fetchall()
        connexion.close()

        factures = []
        for data in factures_data:
            facture = Facture(
                id=data[0],
                patient_id=data[1],
                date_emission=datetime.datetime.strptime(data[2], "%Y-%m-%d").date() if data[2] else None,
                description=data[3],
                statut=data[4],
                date_paiement=datetime.datetime.strptime(data[5], "%Y-%m-%d").date() if data[5] else None
            )
            factures.append(facture)
        
        return factures
    
    @staticmethod
    def updateFactureStatus(facture_id, new_statut="IMPAYE", date_paiement=None):
        connexion = sqlite3.connect(DB_PATH)
        cursor = connexion.cursor()

        cursor.execute(
            "UPDATE facture SET statut = ?, date_paiement = ? WHERE id = ?",
            (new_statut, date_paiement, facture_id)
        )
        connexion.commit()
        connexion.close()

    @staticmethod
    def deleteFacture(facture_id):
        connexion = sqlite3.connect(DB_PATH)
        cursor = connexion.cursor()

        cursor.execute("DELETE FROM facture WHERE id = ?", (facture_id,))
        connexion.commit()
        connexion.close()
        
    @staticmethod
    def getFacturesImpayeByPatientId(patient_id):
        connexion = sqlite3.connect(DB_PATH)
        cursor = connexion.cursor()

        cursor.execute("SELECT * FROM facture WHERE statut = 'IMPAYE' AND patient_id = ?", (patient_id,))
        factures_data = cursor.fetchall()
        connexion.close()

        factures = []
        for data in factures_data:
            facture = Facture(
                id=data[0],
                patient_id=data[1],
                date_emission=datetime.datetime.strptime(data[2], "%Y-%m-%d").date() if data[2] else None,
                description=data[3],
                statut=data[4],
                date_paiement=datetime.datetime.strptime(data[5], "%Y-%m-%d").date() if data[5] else None
            )
            factures.append(facture)
        
        return factures
    
    @staticmethod
    def generate_numero_facture(date_emission=None):
        """
        Génère un numéro de facture du type FAC-AAAA-MM-XXX
        où XXX est le numéro croissant pour le mois AAAA-MM
        """
        if date_emission is None:
            date_emission = datetime.date.today()
        annee_mois = date_emission.strftime('%Y-%m')
        prefix = f"FAC-{annee_mois}-"
        connexion = sqlite3.connect(DB_PATH)
        cursor = connexion.cursor()
        cursor.execute("SELECT id FROM facture WHERE id LIKE ? ORDER BY id DESC", (prefix + '%',))
        facture = cursor.fetchone()
        connexion.close()
        # Extraire les XXX existants
        num = int(facture[0].split('-')[-1]) if facture else 0
        next_num = num + 1
        return f"{prefix}{str(next_num).zfill(3)}"