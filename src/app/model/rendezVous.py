from app.database.setup_db import DB_PATH
import sqlite3
from datetime import datetime,timedelta

from datetime import datetime
from app.model.typeRDV import TypeRDV
import json

from app.services.internet_API_thread_worker import APIRequestQueue


class RendezVous:
    id: int | None
    patient_id: int
    date: datetime
    motif: str
    type_id: int
    presence: str
    facture_id: str
    google_calendar_id: str

    def __init__(
        self,
        patient_id: int,
        date: datetime,
        motif: str,
        type_id: int,
        presence: str,
        facture_id: str = "-1",
        id: int | None = None,
        google_calendar_id: str = ""
    ) -> None:
        """
        Initialise une instance de RendezVous.

        Args:
            patient_id (int): Identifiant du patient.
            date (datetime): Date et heure du rendez-vous.
            motif (str): Motif du rendez-vous.
            type_id (int): Identifiant du type de rendez-vous.
            presence (str): Statut de présence ('présent', 'absent', etc.).
            facture_id (str, optionnel): Identifiant de la facture associée.
            id (int | None, optionnel): Identifiant unique du rendez-vous.
        """
        self.id = id
        self.patient_id = patient_id
        self.date = date
        self.motif = motif
        self.type_id = type_id
        self.presence = presence
        self.facture_id = facture_id
        self.google_calendar_id = google_calendar_id


    def __repr__(self) -> str:
        """
        Retourne une représentation textuelle du rendez-vous.

        Returns:
            str: Représentation lisible du rendez-vous.
        """
        return f"RendezVous(ID: {self.id}, Patient ID: {self.patient_id}, Date: {self.date}, Motif: {self.motif}, Type ID: {self.type_id})"
    def serialize(self) -> dict:
        """
        Sérialise l'objet RendezVous en dictionnaire.

        Returns:
            dict: Dictionnaire représentant le rendez-vous.
        """
        return json.dumps({
            "id": self.id,
            "patient_id": self.patient_id,
            "date": self.date.isoformat() if isinstance(self.date, datetime) else str(self.date),
            "motif": self.motif,
            "type_id": self.type_id,
            "presence": self.presence,
            "facture_id": self.facture_id,
            "google_calendar_id": self.google_calendar_id
        })
    
    @staticmethod
    def parse(serialized_str: str) -> 'RendezVous':
        """
        Désérialise une chaîne JSON en objet RendezVous.

        Args:
            serialized_str (str): Chaîne JSON représentant le rendez-vous.

        Returns:
            RendezVous: Instance de RendezVous.
        """
        data = json.loads(serialized_str)
        date_parsed = datetime.fromisoformat(data["date"]) if "T" in data["date"] else datetime.strptime(data["date"], '%Y-%m-%d %H:%M:%S')
        return RendezVous(
            id=data.get("id"),
            patient_id=data["patient_id"],
            date=date_parsed,
            motif=data["motif"],
            type_id=data["type_id"],
            presence=data["presence"],
            facture_id=data.get("facture_id", "-1"),
            google_calendar_id=data.get("google_calendar_id", "")
        )
    @staticmethod
    def getAllRendezVous() -> list['RendezVous']:
        """
        Récupère tous les rendez-vous de la base de données.

        Returns:
            list[RendezVous]: Liste de tous les rendez-vous.
        """
        connexion = sqlite3.connect(DB_PATH)
        cursor = connexion.cursor()
        cursor.execute("SELECT * FROM rendez_vous")
        rdv_data = cursor.fetchall()
        connexion.close()
        return RendezVous.data_to_rendezvous(rdv_data)
    
    @staticmethod
    def getRendezVousById(rdv_id: int) -> 'RendezVous | None':
        """
        Récupère un rendez-vous par son identifiant.

        Args:
            rdv_id (int): Identifiant du rendez-vous.

        Returns:
            RendezVous | None: Instance de RendezVous si trouvée, sinon None.
        """
        connexion = sqlite3.connect(DB_PATH)
        cursor = connexion.cursor()
        cursor.execute("SELECT * FROM rendez_vous WHERE id = ?", (rdv_id,))
        data = cursor.fetchall()
        connexion.close()
        return RendezVous.data_to_rendezvous(data)[0] if data else None
    
    @staticmethod
    def getRendezVousByPatientId(patient_id: int) -> list['RendezVous']:
        """
        Récupère tous les rendez-vous d'un patient.

        Args:
            patient_id (int): Identifiant du patient.

        Returns:
            list[RendezVous]: Liste des rendez-vous du patient.
        """
        connexion = sqlite3.connect(DB_PATH)
        cursor = connexion.cursor()
        cursor.execute("SELECT * FROM rendez_vous WHERE patient_id = ?", (patient_id,))
        rdv_data = cursor.fetchall()
        connexion.close()
        return RendezVous.data_to_rendezvous(rdv_data)
    
    @staticmethod
    def getRendezVousByPlage(date_debut: datetime, date_fin: datetime) -> list['RendezVous']:
        """
        Récupère tous les rendez-vous dans une plage de dates.

        Args:
            date_debut (datetime): Date de début (format SQL ou ISO).
            date_fin (datetime): Date de fin (format SQL ou ISO).

        Returns:
            list[RendezVous]: Liste des rendez-vous dans la plage.
        """
        connexion = sqlite3.connect(DB_PATH)
        cursor = connexion.cursor()
        cursor.execute("SELECT * FROM rendez_vous WHERE date BETWEEN ? AND ?", (date_debut.strftime('%Y-%m-%d %H:%M:%S'), date_fin.strftime('%Y-%m-%d %H:%M:%S')))
        rdv_data = cursor.fetchall()
        connexion.close()
        return RendezVous.data_to_rendezvous(rdv_data)
    
    @staticmethod
    def addRendezVous(rdv: 'RendezVous') -> None:
        """
        Ajoute un rendez-vous à la base de données.

        Args:
            rdv (RendezVous): Instance du rendez-vous à ajouter.
        """
        try :

            connexion = sqlite3.connect(DB_PATH)
            cursor = connexion.cursor()

            # store date as standardized string to match data_to_rendezvous parsing
            date_str = rdv.date.strftime('%Y-%m-%d %H:%M:%S') if isinstance(rdv.date, datetime) else str(rdv.date)

            cursor.execute(
                "INSERT INTO rendez_vous (patient_id, date, motif, type_id, presence, facture_id) VALUES (?, ?, ?, ?, ?, ?)",
                (rdv.patient_id, date_str, rdv.motif, rdv.type_id, rdv.presence, rdv.facture_id)
            )
            rdv.id = cursor.lastrowid
            connexion.commit()
            connexion.close()
        except Exception as e :
            print(f"[ERREUR] {e}")
            return
        try :
            APIRequestQueue.enqueue_api_request('calendar_create_event', rdv.serialize())
        except Exception as e :
            print(f"[ERREUR CALENDAR] {e}")
            return

    @staticmethod
    def updateRendezVous(rdv_id: int, new_rdv: 'RendezVous') -> None:
        """
        Met à jour un rendez-vous existant dans la base de données.

        Args:
            rdv_id (int): Identifiant du rendez-vous à mettre à jour.
            rdv (RendezVous): Nouvelle instance du rendez-vous.
        """
        from app.services.calendar_api import modify_rdv
        try : 
            connexion = sqlite3.connect(DB_PATH)
            cursor = connexion.cursor()
            old_rdv = RendezVous.getRendezVousById(rdv_id)
            cursor.execute(
                "UPDATE rendez_vous SET patient_id = ?, date = ?, motif = ?, type_id = ?, presence= ?, facture_id=?, google_calendar_id=? WHERE id = ?",
                (new_rdv.patient_id, new_rdv.date, new_rdv.motif, new_rdv.type_id, new_rdv.presence, new_rdv.facture_id, new_rdv.google_calendar_id, rdv_id)
            )
            connexion.commit()
            connexion.close()
        except Exception as e :
            print(f"[ERREUR] {e}")
            return
        try :
            if (old_rdv.patient_id != new_rdv.patient_id) or (old_rdv.date != new_rdv.date) or (old_rdv.motif != new_rdv.motif) or (old_rdv.type_id != new_rdv.type_id) :
                APIRequestQueue.enqueue_api_request('calendar_modify_rdv', new_rdv.serialize())

        except Exception as e :
            print(f"[ERREUR CALENDAR] {e}")
            return

    @staticmethod
    def getRendezVousByDateTime(date_time: datetime) -> list['RendezVous']:
        """
        Récupère tous les rendez-vous à une date/heure précise.

        Args:
            date_time (datetime): Date et heure recherchées.

        Returns:
            list[RendezVous]: Liste des rendez-vous à cette date/heure.
        """
        connexion = sqlite3.connect(DB_PATH)
        cursor = connexion.cursor()
        cursor.execute("SELECT * FROM rendez_vous WHERE date = ?", (date_time.strftime('%Y-%m-%d %H:%M:%S'),))
        data = cursor.fetchall()
        connexion.close()
        return RendezVous.data_to_rendezvous(data)
    
    @staticmethod
    def creneauLibre(rendezvous: 'RendezVous') -> bool:
        """
        Vérifie si un créneau est libre pour un rendez-vous donné.

        Args:
            rendezvous (RendezVous): Rendez-vous à vérifier.

        Returns:
            bool: True si le créneau est libre, False sinon.
        """
        connexion = sqlite3.connect(DB_PATH)
        cursor = connexion.cursor()
        type_rdv: TypeRDV = cursor.execute("SELECT * FROM type_rdv WHERE id = ?", (rendezvous.type_id,)).fetchall()[0]
        duree = int(type_rdv[4])
        dureetime: timedelta= timedelta(minutes=duree)
        date_fin :str = (rendezvous.date + dureetime).strftime('%Y-%m-%d %H:%M:%S')
        date_debut :str = rendezvous.date.strftime('%Y-%m-%d %H:%M:%S')
        cursor.execute("""
                SELECT * FROM rendez_vous r, type_rdv t
                WHERE r.type_id = t.id AND (
                       date <= ? and datetime(date, '+' || duree || ' minutes') > ?
                       OR
                       date >= ? and datetime(date, '+' || duree || ' minutes') <= ?
                       OR
                       date < ? and datetime(date, '+' || duree || ' minutes') > ?
                       OR
                       date <= ? and datetime(date, '+' || duree || ' minutes') >= ?
                      )
                       AND r.id != ?
        """, (date_debut, date_debut,
              date_debut,date_fin,
              date_fin,date_fin,
              date_debut,date_fin,
              rendezvous.id if rendezvous.id is not None else -1))
        # l'id du rendez-vous est exclu de la vérification pour les modifications -1 signifie qu'on ajoute un nouveau rdv
        rdv_data = cursor.fetchall()
        connexion.close()
        
        # si c'est un type groupé il faut vérifier que tous les rendez vous sont en même temps
        if (type_rdv[7]) :

            rdv = []
            for data in rdv_data :
                # on vérifie que tous les rdv sont du même type
                if (int(data[4])!=rendezvous.type_id):
                    return False
            # si tous les rdv sont du même type et que c'est une séance groupée
            return True
        # si ce n'est pas un rendez-vous groupé siil y à un autre rdv sur le créneau ce n'est pas libre
        else :

            if (not rdv_data):
                return True
            return False
        
    @staticmethod
    def getRendezVousByPatientAndDateRange(patient_id: int, start_date: datetime, end_date: datetime) -> list['RendezVous']:
        """
        Récupère tous les rendez-vous d'un patient dans une plage de dates.

        Args:
            patient_id (int): Identifiant du patient.
            start_date (datetime): Date de début.
            end_date (datetime): Date de fin.

        Returns:
            list[RendezVous]: Liste des rendez-vous du patient dans la plage.
        """
        connexion = sqlite3.connect(DB_PATH)
        cursor = connexion.cursor()
        cursor.execute("SELECT * FROM rendez_vous WHERE patient_id = ? AND date BETWEEN ? AND ?", (patient_id, start_date.strftime('%Y-%m-%d %H:%M:%S'), end_date.strftime('%Y-%m-%d %H:%M:%S')))
        rdv_data = cursor.fetchall()
        connexion.close()
        return RendezVous.data_to_rendezvous(rdv_data)
    
    @staticmethod
    def getRendezVousByFactureId(facture_id: str) -> list['RendezVous']:
        """
        Récupère tous les rendez-vous d'une facture.

        Args:
            facture_id (str): Identifiant de la facture.

        Returns:
            list[RendezVous]: Liste des rendez-vous de la facture.
        """
        connexion = sqlite3.connect(DB_PATH)
        cursor = connexion.cursor()

        cursor.execute("SELECT * FROM rendez_vous WHERE facture_id = ?", (facture_id,))
        rdv_data = cursor.fetchall()
        connexion.close()

        return RendezVous.data_to_rendezvous(rdv_data)
    
    @staticmethod
    def data_to_rendezvous(data: list[str]) -> list['RendezVous']:
        """
        Convertit une liste de tuples SQL en objets RendezVous.

        Args:
            data (list): Liste de tuples représentant les lignes SQL.

        Returns:
            list[RendezVous]: Liste d'instances RendezVous.
        """
        rdvs: list[RendezVous] = []
        if (data is None or data==[]):
            return rdvs
        
        for row in data:
            rdv = RendezVous(
                id=row[0],
                patient_id=row[1],
                date=datetime.strptime(row[2], '%Y-%m-%d %H:%M:%S'),
                motif=row[3],
                type_id=row[4],
                presence=row[5],
                facture_id=row[6]
                ,google_calendar_id=row[7]
            )
            rdvs.append(rdv)

        print(f"Converted {len(rdvs)} rows to RendezVous instances.")

        return rdvs