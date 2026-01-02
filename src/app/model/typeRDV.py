from app.database.setup_db import DB_PATH
import sqlite3
import traceback
from datetime import timedelta

class TypeRDV:
    id: int
    nom: str
    description: str
    prix: float
    duree: timedelta
    localisation: str
    couleur: str
    estgroupe: bool

    def __init__(self, id: int, nom: str, description: str, prix: float, duree: 'timedelta', localisation: str, couleur: str, estgroupe: bool) -> None:
        """
        Initialise une instance de TypeRDV.

        Args:
            id (int): Identifiant du type de rendez-vous.
            nom (str): Nom du type de rendez-vous.
            description (str): Description du type de rendez-vous.
            prix (float): Prix du rendez-vous.
            duree (timedelta): Durée du rendez-vous.
            localisation (str): Lieu du rendez-vous.
            couleur (str): Couleur associée.
            estgroupe (bool): Indique si le rendez-vous est groupé.
        """
        self.id = id
        self.nom = nom
        self.description = description
        self.prix = prix
        self.duree = duree
        self.localisation = localisation
        self.couleur = couleur
        self.estgroupe = estgroupe

    def __repr__(self) -> str:
        """
        Retourne une représentation textuelle du type de rendez-vous.

        Returns:
            str: Représentation lisible du type de rendez-vous.
        """
        return f"TypeRDV(ID: {self.id}, Nom: {self.nom}, Description: {self.description}, Prix: {self.prix})"
    
    @staticmethod
    def getAllTypesRDV() -> list['TypeRDV']:
        """
        Récupère tous les types de rendez-vous depuis la base de données.

        Returns:
            list[TypeRDV]: Liste de tous les types de rendez-vous.
        """
        connexion = sqlite3.connect(DB_PATH)
        cursor = connexion.cursor()
        cursor.execute("SELECT * FROM type_rdv")
        types_data = cursor.fetchall()
        connexion.close()
        types = []
        for data in types_data:
            type_rdv = TypeRDV(
                id=data[0],
                nom=data[1],
                description=data[2],
                prix=data[3],
                duree=timedelta(minutes=int(data[4])),
                localisation=data[5],
                couleur=data[6],
                estgroupe=data[7]
            )
            types.append(type_rdv)
        return types
    
    @staticmethod
    def getTypeRDVById(type_id: int) -> 'TypeRDV | None':
        """
        Récupère un type de rendez-vous par son identifiant.

        Args:
            type_id (int): Identifiant du type de rendez-vous.

        Returns:
            TypeRDV | None: Instance de TypeRDV si trouvée, sinon None.
        """
        connexion = sqlite3.connect(DB_PATH)
        cursor = connexion.cursor()
        cursor.execute("SELECT * FROM type_rdv WHERE id = ?", (type_id,))
        data = cursor.fetchone()
        connexion.close()
        if data:
            return TypeRDV(
                id=data[0],
                nom=data[1],
                description=data[2],
                prix=data[3],
                duree=timedelta(minutes=int(data[4])),
                localisation=data[5],
                couleur=data[6],
                estgroupe=data[7]
            )
        return None
    
    @staticmethod
    def addTypeRDV(typeRDV: 'TypeRDV') -> None:
        """
        Ajoute un type de rendez-vous à la base de données.

        Args:
            typeRDV (TypeRDV): Instance du type de rendez-vous à ajouter.
        """
        connexion = sqlite3.connect(DB_PATH)
        cursor = connexion.cursor()
        cursor.execute(
            "INSERT INTO type_rdv (nom, description, prix, duree, localisation, couleur,estgroupe) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (typeRDV.nom, typeRDV.description, typeRDV.prix, typeRDV.duree.total_seconds() // 60, typeRDV.localisation, typeRDV.couleur, typeRDV.estgroupe)
        )
        connexion.commit()
        connexion.close()
    
    @staticmethod
    def updateTypeRDV(new_type_rdv: 'TypeRDV') -> None:
        """Mettre à jour un type de RDV
        Args:
            type_rdv (TypeRDV): Instance du type de rendez-vous à mettre à jour.
        """
        connexion = sqlite3.connect(DB_PATH)
        cursor = connexion.cursor()
        old_type = TypeRDV.getTypeRDVById(new_type_rdv.id)
        cursor.execute("""
            UPDATE type_rdv 
            SET nom = ?, description = ?, prix = ?, duree = ?, localisation = ?, couleur = ?, estgroupe = ?
            WHERE id = ?
        """, (new_type_rdv.nom, new_type_rdv.description, new_type_rdv.prix, new_type_rdv.duree.total_seconds() // 60, new_type_rdv.localisation, new_type_rdv.couleur, new_type_rdv.estgroupe, new_type_rdv.id))
        connexion.commit()
        connexion.close()
        if (old_type.duree != new_type_rdv.duree) or (old_type.nom != new_type_rdv.nom):
            from app.model.rendezVous import RendezVous
            from app.services.internet_API_thread_worker import APIRequestQueue
            rendezvous_list = RendezVous.getRendezVousByTypeId(new_type_rdv.id)
            for rdv in rendezvous_list:
                try : 
                    APIRequestQueue.enqueue_api_request('calendar_modify_rdv', rdv.serialize())
                except Exception as e:
                    print(f"[ERREUR CALENDAR] {e}")
                    traceback.print_exc()
    
    @staticmethod
    def deleteTypeRDV(type_rdv_id: int) -> None:
        """Supprimer un type de RDV
        Args:
            type_rdv_id (int): Identifiant du type de rendez-vous à supprimer.
        """
        connexion = sqlite3.connect(DB_PATH)
        cursor = connexion.cursor()
        cursor.execute("DELETE FROM type_rdv WHERE id = ?", (type_rdv_id,))
        connexion.commit()
        connexion.close()