from os import path, environ, makedirs
from sqlalchemy import inspect, text
from app.backend.database.database import DB_PATH

# Même logique de chemin que setup_db.py


def ensure_db():

    from app.backend.database.database import engine, Base
    import app.backend.model.patient
    import app.backend.model.rendezVous
    import app.backend.model.typeRDV
    import app.backend.model.facture
    import app.backend.model.ligneFacture
    import app.backend.model.contact
    
    if not path.exists(DB_PATH):
        makedirs(path.dirname(DB_PATH), exist_ok=True)
        # Créer le fichier .db vide s'il n'existe pas
        open(DB_PATH, 'a').close()
        print(f"[update_schema] Base de données créée: {DB_PATH}")

    # 1. Créer les tables qui n'existent pas encore
    # SQLAlchemy est intelligent : il ne touche pas aux tables qui ont déjà vos données !
    Base.metadata.create_all(engine)
    print("[update_schema] Vérification du schéma...")

    # 2. Inspecter la base de données actuelle pour y ajouter les éventuelles nouvelles colonnes
    inspector = inspect(engine)
    
    with engine.begin() as conn:
        # On parcourt tous vos modèles (classes Python)
        for table_name, table_metadata in Base.metadata.tables.items():
            # On récupère les colonnes qui existent physiquement dans SQLite
            db_columns = [col['name'] for col in inspector.get_columns(table_name)]
            
            # On compare avec les colonnes de vos fichiers .py
            for model_column in table_metadata.columns:
                if model_column.name not in db_columns:
                    # La colonne est dans le code mais pas dans la DB : on l'ajoute !
                    col_type = model_column.type.compile(engine.dialect)
                    alter_sql = f'ALTER TABLE "{table_name}" ADD COLUMN "{model_column.name}" {col_type}'
                    
                    try:
                        print(f" -> Ajout de la colonne manquante : {table_name}.{model_column.name} ({col_type})")
                        conn.execute(text(alter_sql))
                    except Exception as e:
                        print(f"Erreur lors de l'ajout de la colonne {model_column.name}: {e}")
                    
    print("[update_schema] Base de données à jour !")

