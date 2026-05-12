from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import declarative_base, sessionmaker
from os import path, environ
from app.backend.services.constantes_manager import get_constante

# Le même chemin que votre ancien setup_db.py pour ne pas perdre les données
DB_PATH = path.join(environ.get('APPDATA', ''), 'CabiLib', 'CabiLib.db').replace('\\', '/')
print(DB_PATH)
SQLALCHEMY_DATABASE_URL = f"sqlite:///{DB_PATH}"

def update_db_path(new_path: str):
    global DB_PATH, SQLALCHEMY_DATABASE_URL
    DB_PATH = new_path
    SQLALCHEMY_DATABASE_URL = f"sqlite:///{DB_PATH}"

    engine = create_engine(
        SQLALCHEMY_DATABASE_URL, 
        connect_args={"check_same_thread": False}
    )
    SessionLocal.configure(bind=engine)

# Création de l'engine de la base de données
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False} # Requis pour SQLite
)

@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

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
