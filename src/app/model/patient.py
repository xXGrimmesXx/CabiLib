import sys
import os
import datetime
# Ajouter le répertoire racine au path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from database.setup_db import DB_PATH
import sqlite3

class Patient:
    def __init__(self,nom, prenom, sexe, date_naissance, adresse, ville, telephone1, typeTelephone1, telephone2, typeTelephone2, email, niveau=None, ecole=None, amenagement=None, etat_suivi=None, description=None,id=0):
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

    def __repr__(self):
        return f"Patient({self.nom} {self.prenom}, {self.sexe})"
    
    @staticmethod
    def getAllPatients():
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
                date_naissance=datetime.datetime.strptime(data[4], "%Y-%m-%d"),
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
    def getPatientById(patient_id):
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
                date_naissance=datetime.datetime.strptime(data[4], "%Y-%m-%d"),
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
        else:
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