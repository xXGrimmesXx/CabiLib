from app.database.setup_db import DB_PATH
import sqlite3


class LigneFacture:
    facture_id: str
    rdv_id: int
    montant_facture: float

    def __init__(self, facture_id: str, rdv_id: int, montant_facture: float) -> None:
        """
        Initialise une instance de LigneFacture.

        Args:
            facture_id (str): Identifiant de la facture associée.
            rdv_id (int): Identifiant du rendez-vous associé.
            montant_facture (float): Montant facturé pour ce rendez-vous.
        """
        self.facture_id = facture_id
        self.rdv_id = rdv_id
        self.montant_facture = montant_facture

        def __repr__(self) -> str:
            """
            Retourne une représentation textuelle de la ligne de facture.

            Returns:
                str: Représentation lisible de la ligne de facture.
            """
            return f"LigneFacture(Facture ID: {self.facture_id}, Rendez-vous ID: {self.rdv_id})"
    
    @staticmethod
    def getAllLignesFacture() -> list['LigneFacture']:
        """
        Récupère toutes les lignes de facture de la base de données.

        Returns:
            list[LigneFacture]: Liste de toutes les lignes de facture.
        """
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
    def getLigneFacture(idFacture: str, idRendezVous: int) -> 'LigneFacture | None':
        """
        Récupère une ligne de facture par identifiants.

        Args:
            idFacture (str): Identifiant de la facture.
            idRendezVous (int): Identifiant du rendez-vous.

        Returns:
            LigneFacture | None: Instance de LigneFacture si trouvée, sinon None.
        """
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
    def addLigneFacture(ligne_facture: 'LigneFacture') -> None:
        """
        Ajoute une ligne de facture à la base de données.

        Args:
            ligne_facture (LigneFacture): Instance de la ligne de facture à ajouter.
        """
        connexion = sqlite3.connect(DB_PATH)
        cursor = connexion.cursor()
        cursor.execute(
            "INSERT INTO ligne_facture (idRendezVous, idFacture, montant_facture) VALUES (?, ?, ?)",
            (ligne_facture.rdv_id, ligne_facture.facture_id, ligne_facture.montant_facture)
        )
        connexion.commit()
        connexion.close()
    
    @staticmethod
    def deleteLigneFacture(idFacture: str, idRendezVous: int) -> None:
        """
        Supprime une ligne de facture de la base de données.

        Args:
            idFacture (str): Identifiant de la facture.
            idRendezVous (int): Identifiant du rendez-vous.
        """
        connexion = sqlite3.connect(DB_PATH)
        cursor = connexion.cursor()
        cursor.execute(
            "DELETE FROM ligne_facture WHERE idFacture = ? AND idRendezVous = ?",
            (idFacture, idRendezVous)
        )
        connexion.commit()
        connexion.close()

    @staticmethod
    def getAllLignesByFactureId(facture_id: str) -> list['LigneFacture']:
        """
        Récupère toutes les lignes de facture associées à une facture donnée.

        Args:
            facture_id (str): Identifiant de la facture.

        Returns:
            list[LigneFacture]: Liste des lignes de facture associées.
        """
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