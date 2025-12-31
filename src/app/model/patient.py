from datetime import datetime
import traceback
from app.database.setup_db import DB_PATH
import sqlite3

class Patient:
    id: int
    nom: str
    prenom: str
    sexe: str
    date_naissance: datetime
    adresse: str
    ville: str
    telephone1: str
    typeTelephone1: str
    telephone2: str
    typeTelephone2: str
    email: str
    niveau: str | None
    ecole: str | None
    amenagement: str | None
    etat_suivi: str | None
    description: str | None

    def __init__(self, nom: str, prenom: str, sexe: str, date_naissance: 'datetime.datetime', adresse: str, ville: str, telephone1: str, typeTelephone1: str, telephone2: str, typeTelephone2: str, email: str, niveau: str = None, ecole: str = None, amenagement: str = None, etat_suivi: str = None, description: str = None, id: int = 0) -> None:
        """
        Initialise une instance de Patient.

        Args:
            nom (str): Nom du patient.
            prenom (str): Prénom du patient.
            sexe (str): Sexe du patient.
            date_naissance (datetime.datetime): Date de naissance du patient.
            adresse (str): Adresse du patient.
            ville (str): Ville du patient.
            telephone1 (str): Premier numéro de téléphone.
            typeTelephone1 (str): Type du premier téléphone.
            telephone2 (str): Deuxième numéro de téléphone.
            typeTelephone2 (str): Type du deuxième téléphone.
            email (str): Adresse email du patient.
            niveau (str | None, optionnel): Niveau scolaire.
            ecole (str | None, optionnel): École.
            amenagement (str | None, optionnel): Aménagements particuliers.
            etat_suivi (str | None, optionnel): État du suivi.
            description (str | None, optionnel): Description complémentaire.
            id (int, optionnel): Identifiant unique du patient.
        """
        self.id = id
        self.nom = nom
        self.prenom = prenom
        self.sexe = sexe
        self.date_naissance = date_naissance
        self.adresse = adresse
        self.ville = ville
        self.telephone1 = telephone1
        self.typeTelephone1 = typeTelephone1
        self.telephone2 = telephone2
        self.typeTelephone2 = typeTelephone2
        self.email = email
        self.niveau = niveau
        self.ecole = ecole
        self.amenagement = amenagement
        self.etat_suivi = etat_suivi
        self.description = description

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
    
    @staticmethod
    def getAllPatients() -> list['Patient']:
        """
        Récupère tous les patients de la base de données.

        Returns:
            list[Patient]: Liste de tous les patients.
        """
        connexion = sqlite3.connect(DB_PATH)
        cursor = connexion.cursor()
        cursor.execute("SELECT * FROM patient")
        patients_data = cursor.fetchall()
        connexion.close()
        patients = []
        for data in patients_data:
            patient = Patient(
                id=data[0],
                nom=data[1],
                prenom=data[2],
                sexe=data[3],
                date_naissance=datetime.strptime(data[4], "%Y-%m-%d"),
                adresse=data[5],
                amenagement=data[6],
                niveau=data[7],
                ecole=data[8],
                ville=data[9],
                telephone1=data[10],
                typeTelephone1=data[11],
                telephone2=data[12],
                typeTelephone2=data[13],
                email=data[14],
                etat_suivi=data[15],
                description=data[16]
            )
            patients.append(patient)
        return patients
    
    @staticmethod
    def getPatientById(patient_id: int) -> 'Patient | None':
        """
        Récupère un patient par son identifiant.

        Args:
            patient_id (int): Identifiant du patient.

        Returns:
            Patient | None: Instance de Patient si trouvée, sinon None.
        """
        connexion = sqlite3.connect(DB_PATH)
        cursor = connexion.cursor()
        cursor.execute("SELECT * FROM patient WHERE id = ?", (patient_id,))
        data = cursor.fetchone()
        connexion.close()
        if data:
            return Patient(
                id=data[0],
                nom=data[1],
                prenom=data[2],
                sexe=data[3],
                date_naissance=datetime.strptime(data[4], "%Y-%m-%d"),
                adresse=data[5],
                amenagement=data[6],
                niveau=data[7],
                ecole=data[8],
                ville=data[9],
                telephone1=data[10],
                typeTelephone1=data[11],
                telephone2=data[12],
                typeTelephone2=data[13],
                email=data[14],
                etat_suivi=data[15],
                description=data[16]
            )
        return None
        
    @staticmethod
    def addPatient(patient):
        try:
            connexion = sqlite3.connect(DB_PATH)
            cursor = connexion.cursor()

            cursor.execute("""
                INSERT INTO patient (nom, prenom, sexe, date_naissance, adresse, amenagement, niveau, ecole, ville, telephone1, typeTelephone1, telephone2, typeTelephone2, email, etat_suivi, description)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (patient.nom, patient.prenom, patient.sexe, patient.date_naissance.strftime("%Y-%m-%d"), patient.adresse, patient.amenagement, patient.niveau, patient.ecole, patient.ville, patient.telephone1, patient.typeTelephone1, patient.telephone2, patient.typeTelephone2, patient.email, patient.etat_suivi, patient.description))
            
            patient_id = cursor.lastrowid  # Récupérer l'ID du patient inséré
            connexion.commit()
            connexion.close()
            
            return patient_id  # Retourner l'ID pour confirmation
        except Exception as e:
            print(f"✗ Erreur lors de l'ajout du patient : {e}")
            traceback.print_exc()
            return None

    @staticmethod
    def updatePatient(patient_id, patient):
        connexion = sqlite3.connect(DB_PATH)
        cursor = connexion.cursor()

        cursor.execute("""
            UPDATE patient
            SET nom = ?, prenom = ?, sexe = ?, date_naissance = ?, adresse = ?, amenagement = ?, niveau = ?, ecole = ?, ville = ?, telephone1 = ?, typeTelephone1 = ?, telephone2 = ?, typeTelephone2 = ?, email = ?, etat_suivi = ?, description = ?
            WHERE id = ?""", (patient.nom, patient.prenom, patient.sexe, patient.date_naissance.strftime("%Y-%m-%d"), patient.adresse, patient.amenagement, patient.niveau, patient.ecole, patient.ville, patient.telephone1, patient.typeTelephone1, patient.telephone2, patient.typeTelephone2, patient.email, patient.etat_suivi, patient.description, patient_id))
        connexion.commit()
        connexion.close()

    @staticmethod
    def deletePatient(patient_id):
        connexion = sqlite3.connect(DB_PATH)
        cursor = connexion.cursor()

        cursor.execute("DELETE FROM patient WHERE id = ?", (patient_id,))
        connexion.commit()
        connexion.close()