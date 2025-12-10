from app.database.setup_db import DB_PATH
import sqlite3
from datetime import datetime

class Facture:

    def __init__(self, id: int, patient_id: int, date_emission: 'datetime.date' = datetime.today().date(), description: str = "", statut: str = "IMPAYE", date_paiement: 'datetime.date' = None) -> None:
        """
        Initialise une instance de Facture.

        Args:
            id (int): Identifiant unique de la facture (ex: FAC-2023-12-001).
            patient_id (int): Identifiant du patient associé à la facture.
            date_emission (datetime.date, optionnel): Date d'émission de la facture. Défaut: aujourd'hui.
            description (str, optionnel): Description de la facture.
            statut (str, optionnel): Statut de la facture (ex: 'IMPAYE', 'PAYE').
            date_paiement (datetime.date, optionnel): Date de paiement si payée.
        """
        self.id = id
        self.patient_id = patient_id
        self.date_emission = date_emission
        self.description = description
        self.statut = statut
        self.date_paiement = date_paiement

    def __repr__(self) -> str:
        """
        Retourne une représentation textuelle de la facture.

        Returns:
            str: Représentation lisible de la facture.
        """
        return f"Facture(ID: {self.id}, Patient ID: {self.patient_id}, Date d'émission: {self.date_emission}, Description: {self.description}, Statut: {self.statut}, Date de paiement: {self.date_paiement})"
    
    @staticmethod
    def addFacture(facture: "Facture") -> str:
        """
        Ajoute une facture à la base de données.

        Args:
            facture (Facture): Instance de la facture à ajouter.

        Returns:
            str: L'identifiant de la facture ajoutée.
        """
        connexion = sqlite3.connect(DB_PATH)
        cursor = connexion.cursor()
        id_fac = Facture.generate_numero_facture(facture.date_emission)
        cursor.execute(
            "INSERT INTO facture (id,patient_id, date_emission, description, statut, date_paiement) VALUES (?, ?, ?, ?, ?, ?)",
            (id_fac, facture.patient_id, facture.date_emission, facture.description, facture.statut, facture.date_paiement)
        )
        connexion.commit()
        connexion.close()
        return id_fac

    @staticmethod
    def getFactureById(facture_id: str) -> 'Facture | None':
        """
        Récupère une facture par son identifiant.

        Args:
            facture_id (str): Identifiant de la facture.

        Returns:
            Facture | None: Instance de Facture si trouvée, sinon None.
        """
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
    def getAllFactures() -> list['Facture']:
        """
        Récupère toutes les factures de la base de données.

        Returns:
            list[Facture]: Liste de toutes les factures.
        """
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
    def updateFactureStatus(facture_id: str, new_statut: str = "IMPAYE", date_paiement: 'datetime.date' = None) -> None:
        """
        Met à jour le statut et la date de paiement d'une facture.

        Args:
            facture_id (str): Identifiant de la facture à mettre à jour.
            new_statut (str, optionnel): Nouveau statut ('IMPAYE', 'PAYE', etc.).
            date_paiement (datetime.date, optionnel): Nouvelle date de paiement.
        """
        connexion = sqlite3.connect(DB_PATH)
        cursor = connexion.cursor()
        cursor.execute(
            "UPDATE facture SET statut = ?, date_paiement = ? WHERE id = ?",
            (new_statut, date_paiement, facture_id)
        )
        connexion.commit()
        connexion.close()

    @staticmethod
    def deleteFacture(facture_id: str) -> None:
        """
        Supprime une facture de la base de données.

        Args:
            facture_id (str): Identifiant de la facture à supprimer.
        """
        connexion = sqlite3.connect(DB_PATH)
        cursor = connexion.cursor()
        cursor.execute("DELETE FROM facture WHERE id = ?", (facture_id,))
        connexion.commit()
        connexion.close()
        
    @staticmethod
    def getFacturesImpayeByPatientId(patient_id: int) -> list['Facture']:
        """
        Récupère toutes les factures impayées d'un patient.

        Args:
            patient_id (int): Identifiant du patient.

        Returns:
            list[Facture]: Liste des factures impayées du patient.
        """
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
    def generate_numero_facture(date_emission: 'datetime.date' = None) -> str:
        """
        Génère un numéro de facture du type FAC-AAAA-MM-XXX où XXX est le numéro croissant pour le mois AAAA-MM.

        Args:
            date_emission (datetime.date, optionnel): Date d'émission de la facture. Défaut: aujourd'hui.

        Returns:
            str: Numéro de facture généré.
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
        num = int(facture[0].split('-')[-1]) if facture else 0
        next_num = num + 1
        return f"{prefix}{str(next_num).zfill(3)}"