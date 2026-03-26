from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from os import path, environ

# Le même chemin que votre ancien setup_db.py pour ne pas perdre les données
DB_PATH = path.join(environ.get('APPDATA', ''), 'CabiLib', 'CabiLib.db').replace('\\', '/')
SQLALCHEMY_DATABASE_URL = f"sqlite:///{DB_PATH}"

# Création de l'engine de la base de données
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False} # Requis pour SQLite
)

# Création de l'usine à sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base pour nos modèles (toutes les classes hériteront de cette Base)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
