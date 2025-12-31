from os import path, environ, makedirs
import sqlite3


# Même logique de chemin que setup_db.py
DB_PATH = path.join(environ.get('APPDATA', '.'), 'CabiLib', 'CabiLib.db').replace('\\', '/')


# Schéma attendu (CREATE TABLE SQL)
TABLE_CREATE_SQL = {
    'patient': (
        "CREATE TABLE patient("
        "id INTEGER PRIMARY KEY AUTOINCREMENT,\n"
        "nom TEXT,\n"
        "prenom TEXT,\n"
        "sexe TEXT,\n"
        "date_naissance DATE,\n"
        "adresse TEXT,\n"
        "Amenagement TEXT,\n"
        "niveau TEXT,\n"
        "ecole TEXT,\n"
        "ville TEXT,\n"
        "telephone1 TEXT,\n"
        "typeTelephone1 TEXT,\n"
        "telephone2 TEXT,\n"
        "typeTelephone2 TEXT,\n"
        "email TEXT,\n"
        "etat_suivi TEXT,\n"
        "description TEXT)"
    ),
    'rendez_vous': (
        "CREATE TABLE rendez_vous("
        "id INTEGER PRIMARY KEY AUTOINCREMENT,\n"
        "patient_id INTEGER,\n"
        "date DATETIME,\n"
        "motif TEXT,\n"
        "type_id INTEGER,\n"
        "presence TEXT,\n"
        "facture_id TEXT,\n"
        "google_calendar_id TEXT,\n"
        "FOREIGN KEY(type_id) REFERENCES type_rdv(id),"
        "FOREIGN KEY(patient_id) REFERENCES patient(id),"
        "FOREIGN KEY(facture_id) REFERENCES facture(id))"
    ),
    'type_rdv': (
        "CREATE TABLE type_rdv("
        "id INTEGER PRIMARY KEY AUTOINCREMENT,\n"
        "nom TEXT,\n"
        "description TEXT,\n"
        "prix REAL,\n"
        "duree INTEGER,\n"
        "localisation TEXT,\n"
        "couleur TEXT,\n"
        "estgroupe BOOL)"
    ),
    'facture': (
        "CREATE TABLE facture("
        "id TEXT PRIMARY KEY,\n"
        "patient_id INTEGER,\n"
        "date_emission DATE,\n"
        "description TEXT,\n"
        "statut TEXT,\n"
        "date_paiement DATE,\n"
        "FOREIGN KEY(patient_id) REFERENCES patient(id))"
    ),
    'ligne_facture': (
        "CREATE TABLE ligne_facture("
        "idRendezVous INTEGER,\n"
        "idFacture TEXT,\n"
        "montant_facture REAL,\n"
        "PRIMARY KEY (idRendezVous, idFacture),\n"
        "FOREIGN KEY(idFacture) REFERENCES facture(id),\n"
        "FOREIGN KEY(idRendezVous) REFERENCES rendez_vous(id))"
    )
}

def parse_columns_from_create(create_sql):
    inside = create_sql[create_sql.find('(')+1:create_sql.rfind(')')]
    parts = [p.strip() for p in inside.split(',\n')]
    cols = {}
    for p in parts:
        up = p.upper()
        if up.startswith('FOREIGN') or up.startswith('PRIMARY'):
            continue
        tokens = p.split()
        if not tokens:
            continue
        name = tokens[0].strip().strip(',')
        typ = tokens[1] if len(tokens) > 1 else ''
        if (typ[-1:] == ')'):
            typ = typ[:-1]
        cols[name] = typ
    return cols


def get_existing_columns(cursor, table):
    cursor.execute(f"PRAGMA table_info({table})")
    return {row[1]: row[2] for row in cursor.fetchall()}


def ensure_table_and_columns(db_path, apply=False):
    if not path.exists(path.dirname(db_path)):
        print(f"Dossier DB absent: {path.dirname(db_path)}")
        return
    if not path.exists(db_path):
        print(f"Fichier DB absent: {db_path} (rien à vérifier)")
        return

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    summary = []

    for table, create_sql in TABLE_CREATE_SQL.items():
        print(f"== Vérification: {table}")
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table,))
        exists = cur.fetchone() is not None
        if not exists:
            summary.append((table, 'missing_table'))
            print(f" - Table manquante: {table}")
            if apply:
                cur.execute(create_sql)
                conn.commit()
                print(f"   -> Table {table} créée")
            continue

        desired = parse_columns_from_create(create_sql)
        existing = get_existing_columns(cur, table)
        missing = [c for c in desired.keys() if c not in existing]
        mismatches = [c for c in desired.keys() if c in existing and existing[c].upper() != (desired[c] or '').upper()]

        if missing:
            summary.append((table, 'missing_columns', missing))
            print(f" - Colonnes manquantes: {missing}")
            if apply:
                for c in missing:
                    sql = f"ALTER TABLE {table} ADD COLUMN {c} {desired[c]}"
                    print(f"   -> Exécution: {sql}")
                    cur.execute(sql)
                conn.commit()
                print(f"   -> Colonnes ajoutées: {missing}")
        else:
            print(" - Aucune colonne manquante")

        if mismatches:
            summary.append((table, 'type_mismatches', mismatches))
            print(f" - Types différents (non modifiés automatiquement): {mismatches}")

    conn.close()
    print('\nRésumé:')
    for s in summary:
        print(' -', s)

def ensure_db(db_path):
    if not path.exists(db_path):
        makedirs(path.dirname(db_path), exist_ok=True)
        #creer le fichier .db vide
        open(db_path, 'a').close()
        print(f"[update_schema] Base de données créée: {db_path}")

    ensure_table_and_columns(db_path, apply=True)
