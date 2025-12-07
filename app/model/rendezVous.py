from database.setup_db import DB_PATH
import sqlite3
from datetime import datetime,timedelta,time

class RendezVous:
    def __init__(self, patient_id, date, motif, type_id, presence, facture_id=-1, id=None):
        self.id = id
        self.patient_id = patient_id
        self.date = date
        self.motif = motif
        self.type_id = type_id
        self.presence = presence
        self.facture_id = facture_id

    def __repr__(self):
        return f"RendezVous(Patient ID: {self.patient_id}, Date: {self.date}, Motif: {self.motif}, Type ID: {self.type_id})"
    
    @staticmethod
    def getAllRendezVous():
        connexion = sqlite3.connect(DB_PATH)
        cursor = connexion.cursor()

        cursor.execute("SELECT * FROM rendez_vous")
        rdv_data = cursor.fetchall()
        connexion.close()

        rdvs = []
        for data in rdv_data:
            rdv = RendezVous(
                id=data[0],
                patient_id=data[1],
                date=datetime.strptime(data[2], '%Y-%m-%d %H:%M:%S'),
                motif=data[3],
                type_id=int(data[4]),
                presence = data[5],
                    facture_id = data[6]
            )
            rdvs.append(rdv)
        
        return rdvs
    
    @staticmethod
    def getRendezVousById(rdv_id):
        connexion = sqlite3.connect(DB_PATH)
        cursor = connexion.cursor()

        cursor.execute("SELECT * FROM rendez_vous WHERE id = ?", (rdv_id,))
        data = cursor.fetchone()
        connexion.close()

        if data:
            return RendezVous(
                id=data[0],
                patient_id=data[1],
                date=datetime.strptime(data[2], '%Y-%m-%d %H:%M:%S'),
                motif=data[3],
                type_id=int(data[4]),
                presence = data[5],
                    facture_id = data[6]
            )
        return None
    
    @staticmethod
    def getRendezVousByPatientId(patient_id):
        connexion = sqlite3.connect(DB_PATH)
        cursor = connexion.cursor()

        cursor.execute("SELECT * FROM rendez_vous WHERE patient_id = ?", (patient_id,))
        rdv_data = cursor.fetchall()
        connexion.close()

        rdvs = []
        for data in rdv_data:
            h,m,s=map(int, data[3].split(':'))
            rdv = RendezVous(
                id=data[0],
                patient_id=data[1],
                date=datetime.strptime(data[2], '%Y-%m-%d %H:%M:%S'),
                duree=timedelta(hours=h, minutes=m, seconds=s),
                motif=data[3],
                type_id=int(data[4]),
                presence= data[5],
                    facture_id = data[6]
            )
            rdvs.append(rdv)
        
        return rdvs
    
    @staticmethod
    def getRendezVousByPlage(date_debut, date_fin):
        connexion = sqlite3.connect(DB_PATH)
        cursor = connexion.cursor()
        cursor.execute("SELECT * FROM rendez_vous WHERE date BETWEEN ? AND ?", (date_debut, date_fin))
        rdv_data = cursor.fetchall()
        connexion.close()
        rdvs = []
        for data in rdv_data:
            rdv = RendezVous(
                id=data[0],
                patient_id=data[1],
                date=datetime.strptime(data[2], '%Y-%m-%d %H:%M:%S'),
                motif=data[3],
                type_id=int(data[4]),
                presence=data[5],
                facture_id = data[6]
            )
            rdvs.append(rdv)

        return rdvs
    
    @staticmethod
    def addRendezVous(rdv):
        connexion = sqlite3.connect(DB_PATH)
        cursor = connexion.cursor()

        cursor.execute(
            "INSERT INTO rendez_vous (patient_id, date, motif, type_id, presence, facture_id) VALUES (?, ?, ?, ?, ?, ?)",
            (rdv.patient_id, rdv.date, rdv.motif, rdv.type_id, rdv.presence, rdv.facture_id)
        )
        connexion.commit()
        connexion.close()

    @staticmethod
    def updateRendezVous(rdv_id, rdv):
        print("Updating RDV:", rdv_id, rdv)
        connexion = sqlite3.connect(DB_PATH)
        cursor = connexion.cursor()
        cursor.execute(
            "UPDATE rendez_vous SET patient_id = ?, date = ?, motif = ?, type_id = ?, presence= ?, facture_id=? WHERE id = ?",
            (rdv.patient_id, rdv.date, rdv.motif, rdv.type_id, rdv.presence, rdv.facture_id, rdv_id)
        )
        connexion.commit()
        connexion.close()

    @staticmethod
    def getRendezVousByDateTime(date_time):
        connexion = sqlite3.connect(DB_PATH)
        cursor = connexion.cursor()

        cursor.execute("SELECT * FROM rendez_vous WHERE date = ?", (date_time.strftime('%Y-%m-%d %H:%M:%S'),))
        data = cursor.fetchall()
        connexion.close()

        if data:
            rdvs = []
            for rdv in data :
                rdvs.append( RendezVous(
                    patient_id=rdv[1],
                    date=datetime.strptime(rdv[2], '%Y-%m-%d %H:%M:%S'),
                    motif=rdv[3],
                    type_id=int(rdv[4]),
                    id=rdv[0],
                    presence=rdv[5],
                    facture_id = rdv[6]
                ))
            return rdvs
        return None
    
    @staticmethod
    def creneauLibre(rendezvous):
        """Vérifie si un créneau est libre pour un rendez-vous"""
        connexion = sqlite3.connect(DB_PATH)
        cursor = connexion.cursor()

        
        type_rdv = cursor.execute("SELECT * FROM type_rdv WHERE id = ?", (rendezvous.type_id,)).fetchone()
        duree = int(type_rdv[4])
        dureetime = timedelta(minutes=duree)
        date_fin = (rendezvous.date + dureetime).strftime('%Y-%m-%d %H:%M:%S')
        date_debut = rendezvous.date.strftime('%Y-%m-%d %H:%M:%S')
        
        cursor.execute("""
                SELECT * FROM rendez_vous r, type_rdv t
                WHERE r.type_id = t.id AND (
                       date <= ? and datetime(date, '+' || duree || ' minutes') > ?
                       OR
                       date >= ? and datetime(date, '+' || duree || ' minutes') < ?
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
        msg = f"\n\n{rendezvous}\n{[[rdv,"\n"] for rdv in rdv_data]}\n\n"
        print(msg)
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
            #print(rdv_data)
            if (not rdv_data):
                return True
            return False
    
    def getRendezVousByPatientAndDateRange(patient_id, start_date, end_date):
        connexion = sqlite3.connect(DB_PATH)
        cursor = connexion.cursor()

        cursor.execute("SELECT * FROM rendez_vous WHERE patient_id = ? AND date BETWEEN ? AND ?", (patient_id, start_date, end_date))
        rdv_data = cursor.fetchall()
        connexion.close()

        rdvs = []
        for data in rdv_data:
            rdv = RendezVous(
                id=data[0],
                patient_id=data[1],
                date=datetime.strptime(data[2], '%Y-%m-%d %H:%M:%S'),
                motif=data[3],
                type_id=int(data[4]),
                presence=data[5],
                facture_id=data[6]
            )
            rdvs.append(rdv)
        
        return rdvs