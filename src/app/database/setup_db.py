import sqlite3
import os

DB_PATH = os.path.join(os.environ['APPDATA'], 'CabiLib', 'CabiLib.db').replace('\\', '/')

def setup_database():
    connexion = sqlite3.connect(DB_PATH)
    cursor = connexion.cursor()

    # Création de la table patient
    cursor.execute("CREATE TABLE patient" \
        "(id INTEGER PRIMARY KEY AUTOINCREMENT," \
        " nom TEXT," \
        " prenom TEXT," \
        " sexe TEXT," \
        "date_naissance DATE," \
        " adresse TEXT," \
        "Amenagement TEXT," \
        "niveau TEXT," \
        "ecole TEXT," \
        "ville TEXT," \
        "telephone1 TEXT," \
        "typeTelephone1 TEXT," \
        "telephone2 TEXT," \
        "typeTelephone2 TEXT," \
        "email TEXT,"
        "etat_suivi TEXT,"
        "description TEXT)")
    
    # Création de la table rendez_vous
    cursor.execute("CREATE TABLE rendez_vous" \
        "(id INTEGER PRIMARY KEY AUTOINCREMENT," \
        " patient_id INTEGER," \
        " date DATETIME," \
        "motif TEXT," \
        "type_id INTEGER," \
        "presence TEXT,"\
        "facture_id TEXT," \
        "FOREIGN KEY(type_id) REFERENCES type_rdv(id)," \
        " FOREIGN KEY(patient_id) REFERENCES patient(id)," \
        " FOREIGN KEY(facture_id) REFERENCES facture(id))")
    
    # Création de la table type_rdv
    cursor.execute("CREATE TABLE type_rdv" \
        "(id INTEGER PRIMARY KEY AUTOINCREMENT," \
        " nom TEXT," \
        " description TEXT," \
        "prix REAL," \
        "duree INTEGER," \
        "localisation TEXT," \
        "couleur TEXT,"\
        "estgroupe BOOL)")
    
    # Création de la table facture
    cursor.execute("CREATE TABLE facture" \
        "(id TEXT PRIMARY KEY," \
        " patient_id INTEGER,"\
        " date_emission DATE,"\
        " description TEXT,"\
        " statut TEXT,"\
        " date_paiement DATE,"\
        " FOREIGN KEY(patient_id) REFERENCES patient(id))")
    
    # Creation de la table ligne_facture (détail des lignes de facture)
    cursor.execute("CREATE TABLE ligne_facture" \
        "(idRendezVous INTEGER ," \
        "idFacture TEXT ," \
        "montant_facture REAL," \
        "PRIMARY KEY (idRendezVous, idFacture)," \
        " FOREIGN KEY(idFacture) REFERENCES facture(id)," \
        " FOREIGN KEY(idRendezVous) REFERENCES rendez_vous(id))")
    
    connexion.commit()
    connexion.close()

def initDB():
    """Initialise la base de données en créant les tables si elles n'existent pas."""
    connexion = sqlite3.connect(DB_PATH)
    cursor = connexion.cursor()
    cursor.execute("DROP TABLE IF EXISTS ligne_facture")
    cursor.execute("DROP TABLE IF EXISTS facture")
    cursor.execute("DROP TABLE IF EXISTS rendez_vous")
    cursor.execute("DROP TABLE IF EXISTS type_rdv")
    cursor.execute("DROP TABLE IF EXISTS patient")
    connexion.commit()
    connexion.close()
    setup_database()

if __name__ == "__main__":
    setup_database()
    print("Base de données et tables créées avec succès.")