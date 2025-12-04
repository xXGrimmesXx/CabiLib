import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database.setup_db import DB_PATH
import sqlite3
import random
from datetime import datetime, timedelta
from utils import constantes_manager
from app.model.rendezVous import RendezVous

def generate_patients(count=100):
    """Génère des patients aléatoires"""
    noms = ["Dupont", "Martin", "Bernard", "Durand", "Leroy", "Moreau", "Simon", "Michel", "Garcia", "Roux",
            "Fournier", "Chevalier", "Blanc", "Garnier", "Lopez", "Faure", "André", "Mercier", "Girard", "Rousseau",
            "Lemoine", "Laurent", "Lefebvre", "Morel", "Fontaine", "Robin", "Vincent", "Boucher", "Moulin", "Perrin",
            "Gauthier", "Picard", "Dufour", "Bertrand", "Colin", "Pierre", "Renard", "Clement", "Boyer", "Schmitt"]
    
    prenoms_m = ["Jean", "Luc", "Paul", "Antoine", "David", "Nicolas", "Julien", "Thomas", "Alexandre", "Pierre",
                 "François", "Marc", "Philippe", "Christophe", "Olivier", "Laurent", "Stéphane", "Éric", "Bruno", "Patrick",
                 "Alain", "Vincent", "Mathieu", "Lucas", "Hugo", "Louis", "Gabriel", "Arthur", "Nathan", "Léo"]
    
    prenoms_f = ["Sophie", "Claire", "Emma", "Julie", "Laura", "Camille", "Alice", "Chloé", "Marie", "Léa",
                 "Sarah", "Pauline", "Céline", "Lucie", "Charlotte", "Manon", "Anaïs", "Lisa", "Émilie", "Marion",
                 "Juliette", "Caroline", "Isabelle", "Florence", "Catherine", "Martine", "Nathalie", "Sylvie", "Anne", "Valérie"]
    
    villes = ["Paris", "Lyon", "Marseille", "Toulouse", "Nice", "Nantes", "Strasbourg", "Bordeaux", "Lille", "Rennes",
              "Reims", "Saint-Étienne", "Toulon", "Angers", "Grenoble", "Dijon", "Nîmes", "Aix-en-Provence", "Le Mans", "Brest",
              "Tours", "Amiens", "Limoges", "Annecy", "Perpignan", "Besançon", "Orléans", "Rouen", "Caen", "Nancy"]
    
    # Utiliser les constantes de l'application
    amenagements = constantes_manager.get_constante("AMENAGEMENTS_OPTIONS")
    niveaux = constantes_manager.get_constante("NIVEAU_SCOLAIRE_OPTIONS")
    ecoles = ["École Primaire Jules Ferry", "Collège Victor Hugo", "Lycée Louis Pasteur", "École Sainte-Marie",
              "Collège Jean Moulin", "Lycée Voltaire", "École des Lilas", "Collège Molière", "Lycée Descartes"]
    etats_suivi = constantes_manager.get_constante("ETAT_SUIVI_OPTIONS")
    
    patients = []
    for i in range(count):
        sexe = random.choice(["M", "F"])
        prenom = random.choice(prenoms_m if sexe == "M" else prenoms_f)
        nom = random.choice(noms)
        date_naissance = datetime.now() - timedelta(days=random.randint(0,20)*365 + random.randint(0, 365))
        adresse = f"{random.randint(1, 999)} Rue {random.choice(['des Fleurs', 'du Parc', 'de la Gare', 'Victor Hugo', 'Jean Jaurès', 'de la République'])}"
        ville = random.choice(villes)
        
        # Téléphones (2 numéros possibles)
        telephone1 = f"0{random.randint(1, 7)}{random.randint(10000000, 99999999)}"
        typeTelephone1 = random.choice(["Mère", "Père", "Tuteur", "Personnel"])
        
        # 70% de chance d'avoir un 2ème téléphone
        if random.random() < 0.7:
            telephone2 = f"0{random.randint(1, 7)}{random.randint(10000000, 99999999)}"
            typeTelephone2 = random.choice(["Mère", "Père", "Tuteur", "Urgence"])
        else:
            telephone2 = None
            typeTelephone2 = None
        
        email = f"{prenom.lower()}.{nom.lower()}{random.randint(1, 999)}@example.com"
        
        # Nouveaux champs
        amenagement = random.choice(amenagements)
        niveau = random.choice(niveaux)
        ecole = random.choice(ecoles)
        etat_suivi = random.choice(etats_suivi)
        descriptions = [
            "Suivi orthophonique pour troubles du langage",
            "Dyslexie - difficultés en lecture",
            "Retard de parole - rééducation en cours",
            "Bégaiement - thérapie comportementale",
            "Trouble de l'articulation",
            "Dysphasie - suivi intensif",
            "Trouble de la voix",
            "Déglutition atypique"
        ]
        description = random.choice(descriptions)
        
        patients.append((nom, prenom, sexe, date_naissance.strftime("%Y-%m-%d"), adresse, 
                        amenagement, niveau, ecole, ville, telephone1, typeTelephone1, 
                        telephone2, typeTelephone2, email, etat_suivi, description))
    
    return patients

def initPatientTestData():
    """Initialise la base de données avec des données de test pour les patients"""
    connexion = sqlite3.connect(DB_PATH)
    cursor = connexion.cursor()

    test_patients = generate_patients(150)
    
    cursor.executemany("""
        INSERT INTO patient (nom, prenom, sexe, date_naissance, adresse, Amenagement, niveau, ecole, ville, telephone1, typeTelephone1, telephone2, typeTelephone2, email, etat_suivi, description)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, test_patients)
    connexion.commit()
    connexion.close()
    print(f"✓ {len(test_patients)} patients insérés")

def initTypeRdvTestData():
    """Initialise les types de rendez-vous"""
    connexion = sqlite3.connect(DB_PATH)
    cursor = connexion.cursor()
    durees = constantes_manager.get_constante("DUREES_RDV")
    test_type_rdv = [
        ("Consultation générale", "Consultation médicale standard", 50.0, random.choice(durees), "A domicile", "#512B2B", random.randint(0,1)==1),
        ("Consultation spécialisée", "Consultation avec un spécialiste", 80.0, random.choice(durees),"Cabinet", "#5FE1AD", random.randint(0,1)==1),
        ("Suivi de traitement", "Rendez-vous de suivi", 45.0, random.choice(durees),"Cabinet", "#0084FF", random.randint(0,1)==1),
        ("Vaccination", "Administration de vaccins", 30.0, random.choice(durees),"Cabinet", "#00FF1E", random.randint(0,1)==1),
        ("Examen médical", "Examen complet de santé", 100.0, random.choice(durees),"Cabinet", "#FFE600", random.randint(0,1)==1),
        ("Urgence", "Consultation d'urgence", 120.0, random.choice(durees),"Cabinet", "#FF0000", random.randint(0,1)==1),
        ("Téléconsultation", "Consultation à distance", 40.0, random.choice(durees),"Cabinet", "#8000FF", random.randint(0,1)==1)
    ]
    
    cursor.executemany("""
        INSERT INTO type_rdv (nom, description, prix, duree, localisation, couleur, estgroupe)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, test_type_rdv)
    
    connexion.commit()
    connexion.close()
    print("✓ Types de RDV insérés")


def initRendezVousTestData():
    """Initialise les rendez-vous de test"""
    connexion = sqlite3.connect(DB_PATH)
    cursor = connexion.cursor()

    # Récupérer le nombre de patients
    cursor.execute("SELECT COUNT(*) FROM patient")
    nb_patients = cursor.fetchone()[0]
    
    # Générer 120 rendez-vous
    test_rendez_vous = []
    start_date = datetime.now()
    start_date = start_date.replace(hour=8, minute=0, second=0, microsecond=0)
    
    motifs = [
        "Consultation générale", "Suivi de traitement", "Consultation spécialisée",
        "Vaccination", "Examen médical", "Urgence", "Téléconsultation",
        "Contrôle de routine", "Résultats d'analyse", "Renouvellement d'ordonnance"
    ]
    
    
    for i in range(300):
        patient_id = random.randint(1, nb_patients)
        rdv_date = start_date + timedelta(days=random.randint(0, 30), hours=random.randint(0, 9), minutes=random.randint(0,4)*15)
        date_heure = rdv_date
        motif = random.choice(motifs)
        type_rdv = random.randint(1, 7)
        presence = random.choice(constantes_manager.get_constante("PRESENCE_OPTION"))
        
        test_rendez_vous.append(RendezVous(patient_id, date_heure, motif, type_rdv, presence))
    for rdv in test_rendez_vous:
        if (RendezVous.creneauLibre(rdv)):
            RendezVous.addRendezVous(rdv)
    
    connexion.commit()
    connexion.close()
    print(f"✓ {len(test_rendez_vous)} rendez-vous insérés")


def initFactureTestData():
    """Initialise les factures de test avec distribution réaliste"""
    connexion = sqlite3.connect(DB_PATH)
    cursor = connexion.cursor()
    
    # Récupérer tous les patients
    cursor.execute("SELECT id FROM patient")
    patient_ids = [row[0] for row in cursor.fetchall()]
    
    # Distribution réaliste:
    # - 40% des patients ont 0 facture (60 patients)
    # - 40% des patients ont 1-2 factures (60 patients)
    # - 20% des patients ont 3-5 factures (30 patients)
    
    random.shuffle(patient_ids)
    patients_sans_facture = patient_ids[:60]  # 40%
    patients_1_2_factures = patient_ids[60:120]  # 40%
    patients_3_5_factures = patient_ids[120:]  # 20%
    
    test_factures = []
    start_date = datetime(2025, 1, 1)
    statuts = ["Payée", "En attente", "En retard", "Annulée"]
    facture_counter = 1
    
    # Patients avec 1-2 factures
    for patient_id in patients_1_2_factures:
        nb_factures = random.randint(1, 2)
        for _ in range(nb_factures):
            facture_id = f"FAC-2025-{str(facture_counter).zfill(4)}"
            date_emission = (start_date + timedelta(days=random.randint(0, 60))).strftime("%Y-%m-%d")
            description = f"Facture pour {random.choice(['consultation générale', 'suivi', 'examen', 'vaccination', 'urgence'])}"
            statut = random.choice(statuts)
            
            if statut == "Payée":
                date_paiement = (datetime.strptime(date_emission, "%Y-%m-%d") + timedelta(days=random.randint(1, 15))).strftime("%Y-%m-%d")
            else:
                date_paiement = None
            
            test_factures.append((facture_id, patient_id, date_emission, description, statut, date_paiement))
            facture_counter += 1
    
    # Patients avec 3-5 factures
    for patient_id in patients_3_5_factures:
        nb_factures = random.randint(3, 5)
        for _ in range(nb_factures):
            facture_id = f"FAC-2025-{str(facture_counter).zfill(4)}"
            date_emission = (start_date + timedelta(days=random.randint(0, 60))).strftime("%Y-%m-%d")
            description = f"Facture pour {random.choice(['consultation générale', 'suivi', 'examen', 'vaccination', 'urgence'])}"
            statut = random.choice(statuts)
            
            if statut == "Payée":
                date_paiement = (datetime.strptime(date_emission, "%Y-%m-%d") + timedelta(days=random.randint(1, 15))).strftime("%Y-%m-%d")
            else:
                date_paiement = None
            
            test_factures.append((facture_id, patient_id, date_emission, description, statut, date_paiement))
            facture_counter += 1
    
    cursor.executemany("""
        INSERT INTO facture (id, patient_id, date_emission, description, statut, date_paiement)
        VALUES (?, ?, ?, ?, ?, ?)
    """, test_factures)
    
    connexion.commit()
    connexion.close()
    print(f"✓ {len(test_factures)} factures insérées")
    print(f"  • {len(patients_sans_facture)} patients sans facture")
    print(f"  • {len(patients_1_2_factures)} patients avec 1-2 factures")
    print(f"  • {len(patients_3_5_factures)} patients avec 3-5 factures")


def initLignesFactureTestData():
    """Initialise les lignes de facture avec plusieurs lignes par facture"""
    connexion = sqlite3.connect(DB_PATH)
    cursor = connexion.cursor()
    
    # Récupérer tous les rendez-vous
    cursor.execute("SELECT id FROM rendez_vous ORDER BY id")
    rdv_ids = [row[0] for row in cursor.fetchall()]
    
    # Récupérer toutes les factures
    cursor.execute("SELECT id FROM facture ORDER BY id")
    facture_ids = [row[0] for row in cursor.fetchall()]
    
    # Distribution réaliste des lignes par facture:
    # - 30% des factures ont 1 ligne
    # - 50% des factures ont 2-3 lignes
    # - 20% des factures ont 4-6 lignes
    
    test_lignes = []
    rdv_index = 0
    
    for facture_id in facture_ids:
        # Déterminer le nombre de lignes pour cette facture
        rand = random.random()
        if rand < 0.3:
            nb_lignes = 1
        elif rand < 0.8:
            nb_lignes = random.randint(2, 3)
        else:
            nb_lignes = random.randint(4, 6)
        
        # Ajouter les lignes pour cette facture
        for _ in range(nb_lignes):
            if rdv_index >= len(rdv_ids):
                break
            test_lignes.append((rdv_ids[rdv_index], facture_id))
            rdv_index += 1
        
        if rdv_index >= len(rdv_ids):
            break
    
    cursor.executemany("""
        INSERT INTO ligne_facture (idRendezVous, idFacture)
        VALUES (?, ?)
    """, test_lignes)
    
    connexion.commit()
    
    # Statistiques
    cursor.execute("""
        SELECT idFacture, COUNT(*) as nb_lignes 
        FROM Lignes_Facture 
        GROUP BY idFacture
    """)
    lignes_stats = cursor.fetchall()
    avg_lignes = sum(nb for _, nb in lignes_stats) / len(lignes_stats) if lignes_stats else 0
    
    connexion.close()
    print(f"✓ {len(test_lignes)} lignes de facture insérées")
    print(f"  • Moyenne de {avg_lignes:.1f} lignes par facture")


def clearAllData():
    """Supprime toutes les données de test (utile pour réinitialiser)"""
    connexion = sqlite3.connect(DB_PATH)
    cursor = connexion.cursor()
    
    # Ordre important à cause des contraintes de clés étrangères
    cursor.execute("DELETE FROM ligne_facture")
    cursor.execute("DELETE FROM facture")
    cursor.execute("DELETE FROM rendez_vous")
    cursor.execute("DELETE FROM type_rdv")
    cursor.execute("DELETE FROM patient")
    
    connexion.commit()
    connexion.close()
    print("✓ Toutes les données supprimées")


def initAllTestData():
    """Initialise toutes les données de test nécessaires"""
    print("Initialisation des données de test...")
    clearAllData()
    # Ordre important : d'abord les tables sans dépendances
    initPatientTestData()
    initTypeRdvTestData()
    initRendezVousTestData()
    initFactureTestData()
    initLignesFactureTestData()
    
    print("\n✅ Toutes les données de test ont été insérées avec succès!")


# Exécuter lors de l'appel direct du script
if __name__ == "__main__":
    initAllTestData()