import sqlite3
from os import path, environ, makedirs
from threading import Thread, Event
from requests import get, RequestException
from json import loads



DB_PATH = path.join(environ.get('APPDATA', '.'), 'CabiLib', 'api_queue.db').replace('\\', '/')

class APIRequestQueueItem:    
    def __init__(self, id :int, service_name:str, payload:str, attempts:int, status:str, created_at:str):
        self.id = id
        self.service_name = service_name
        self.payload = payload
        self.attempts = attempts
        self.status = status
        self.created_at = created_at

    
class APIRequestQueue:

    def __init__(self):
        self.init_database()

    @staticmethod
    def init_database():
        if not path.exists(path.dirname(DB_PATH)):
            makedirs(path.dirname(DB_PATH))
        if not path.exists(DB_PATH):
            open(DB_PATH, 'a').close()
            print(f"[update_schema] Base de données créée: {DB_PATH}")
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Crée la table si elle n'existe pas
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS api_queue (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                service_name TEXT NOT NULL,
                payload TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                attempts INTEGER DEFAULT 0,
                status TEXT DEFAULT 'pending'  -- 'pending', 'sent', 'failed'
            )
        ''')
        
        conn.commit()
        conn.close()
        
    @staticmethod
    def enqueue_api_request(service_name, payload):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO api_queue (service_name, payload)
            VALUES (?, ?)
        ''', (service_name, payload))
        
        conn.commit()
        conn.close()

    @staticmethod
    def dequeue_api_request(max_attempts=3):
        """
        Récupère la prochaine requête à traiter dans l'ordre chronologique.
        Inclut les requêtes 'pending' et 'failed' (si attempts < max_attempts).
        
        Args:
            max_attempts: Nombre max de tentatives
            
        Returns:
            APIRequestQueueItem ou None si queue vide
        """
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, service_name, payload, attempts, status, created_at
            FROM api_queue
            WHERE (status = 'pending' OR (status = 'failed' AND attempts < ?))
            ORDER BY created_at ASC
            LIMIT 1
        ''', (max_attempts,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return APIRequestQueueItem(*row)
        else:
            return None
        
    @staticmethod
    def update_api_request_status(request_id, status, max_attempts=10):
        """
        Met à jour le statut d'une requête API.
        
        Args:
            request_id: ID de la requête
            status: 'sent' (supprime), 'failed' (incrémente attempts), 'pending' (réinitialise)
            max_attempts: Nombre max de tentatives avant suppression définitive (défaut: 3)
        """
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        try:
            if status not in ('pending', 'sent', 'failed'):
                raise ValueError("Status must be 'pending', 'sent', or 'failed'")
            
            if status == 'sent':
                # Requête réussie: supprimer de la queue
                cursor.execute('DELETE FROM api_queue WHERE id = ?', (request_id,))
                print(f"[API Queue] Requête {request_id} traitée avec succès et supprimée")
                
            elif status == 'failed':
                # Incrémenter les tentatives
                cursor.execute('''
                    UPDATE api_queue
                    SET status = 'failed', attempts = attempts + 1
                    WHERE id = ?
                ''', (request_id,))
                
                # Vérifier si on dépasse le max de tentatives
                cursor.execute('SELECT attempts FROM api_queue WHERE id = ?', (request_id,))
                row = cursor.fetchone()
                if row and row[0] >= max_attempts:
                    cursor.execute('DELETE FROM api_queue WHERE id = ?', (request_id,))
                    print(f"[API Queue] Requête {request_id} supprimée après {row[0]} tentatives échouées")
                else:
                    print(f"[API Queue] Requête {request_id} échouée (tentative {row[0] if row else 0}/{max_attempts})")
                    
            elif status == 'pending':
                # Remettre en pending (réinitialiser)
                cursor.execute('''
                    UPDATE api_queue
                    SET status = 'pending', attempts = 0
                    WHERE id = ?
                ''', (request_id,))
                print(f"[API Queue] Requête {request_id} remise en pending")
            
            conn.commit()
            
        except Exception as e:
            print(f"[API Queue] Erreur lors de la mise à jour du statut: {e}")
            traceback.print_exc()
            conn.rollback()
        finally:
            conn.close()

    @staticmethod
    def check_connection()-> bool:
        """Vérifie si une connexion Internet est disponible."""
        try:
            response = get('https://www.google.com', timeout=5)
            return response.status_code == 200
        except RequestException:
            traceback.print_exc()
            return False

    @staticmethod
    def process_queue(max_attempts=3)-> bool:
        """
        Traite UNE SEULE requête de la queue dans l'ordre chronologique strict.
        
        Args:
            max_attempts: Nombre max de tentatives avant suppression (défaut: 3)
            
        Returns:
            bool: True si traité avec succès ou queue vide, False si pas de connexion Internet.
        """
        # Vérifier la connexion Internet d'abord
        if not APIRequestQueue.check_connection():
            print("[API Queue] Pas de connexion Internet disponible")
            return False
        
        # Récupérer la prochaine requête dans l'ordre
        item = APIRequestQueue.dequeue_api_request(max_attempts)
        if item is None:
            return True  # Queue vide
        
        print(f"[API Queue] Traitement requête {item.id}: {item.service_name} (tentative {item.attempts + 1}/{max_attempts})")
        
        try:
            # Router vers le bon service
            if item.service_name == 'gmail_send_email':
                from app.services.mail_sender import send_email

                #convertir le payload json en dict
                item.payload = loads(item.payload)

                send_email(item.payload)
                APIRequestQueue.update_api_request_status(item.id, 'sent', max_attempts)

            elif item.service_name == 'gmail_save_draft':
                from app.services.mail_sender import save_draft

                #convertir le payload json en dict
                item.payload = loads(item.payload)

                save_draft(item.payload)
                APIRequestQueue.update_api_request_status(item.id, 'sent', max_attempts)

            elif item.service_name == 'calendar_create_event':
                from app.services.calendar_api import insert_rdv
                from app.model.rendezVous import RendezVous
                
                #convertir le payload json en dict
                rdv = RendezVous.parse(item.payload)

                insert_rdv(rdv)
                APIRequestQueue.update_api_request_status(item.id, 'sent', max_attempts)

            elif item.service_name == 'calendar_modify_rdv':
                from app.services.calendar_api import modify_rdv
                from app.model.rendezVous import RendezVous

                #convertir le payload json en dict
                rdv = RendezVous.parse(item.payload)
                modify_rdv(rdv)
                APIRequestQueue.update_api_request_status(item.id, 'sent', max_attempts)

            else:
                print(f"[API Queue] Service inconnu: {item.service_name}")
                APIRequestQueue.update_api_request_status(item.id, 'failed', max_attempts)

        except Exception as e:
            print(f"[API Queue] Erreur lors du traitement de la requête {item.id}: {e}")
            traceback.print_exc()
            APIRequestQueue.update_api_request_status(item.id, 'failed', max_attempts)
        
        return True


class APIWorkerThread:
    """Thread worker qui traite la queue API en arrière-plan."""
    
    def __init__(self, check_interval=10,retry_interval=60):
        """
        Args:
            check_interval: Intervalle en secondes entre les vérifications de la queue (défaut: 10s)
        """
        self.check_interval = check_interval
        self.retry_interval = retry_interval
        self._stop_event = Event()
        self._thread = None
        self._is_running = False
    
    def start(self):
        """Démarre le worker thread."""
        if self._is_running:
            print("[APIWorker] Thread déjà en cours d'exécution")
            return
        
        APIRequestQueue.init_database()
        self._stop_event.clear()
        self._thread = Thread(target=self._run, daemon=True)
        self._thread.start()
        self._is_running = True
        print("[APIWorker] Thread démarré")
    
    def stop(self, timeout=5):
        """Arrête le worker thread."""
        if not self._is_running:
            return
        
        print("[APIWorker] Arrêt du thread...")
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=timeout)
        self._is_running = False
        print("[APIWorker] Thread arrêté")
    
    def _run(self):
        """Boucle principale du worker thread."""
        print("[APIWorker] Boucle de traitement démarrée")
        
        while not self._stop_event.is_set():
            try:
                # Traiter la queue
                result = APIRequestQueue.process_queue()
                
                if result is False:
                    print(f"[APIWorker] Pas de connexion Internet, nouvelle tentative dans {self.retry_interval}s...")
                    self._stop_event.wait(self.retry_interval)  # Attendre plus longtemps si pas de connexion
                else:
                    # Queue traitée avec succès, attendre l'intervalle normal
                    self._stop_event.wait(self.check_interval)
                    
            except Exception as e:
                print(f"[APIWorker] Erreur dans la boucle de traitement: {e}")
                traceback.print_exc()
                self._stop_event.wait(self.check_interval)
        
        print("[APIWorker] Boucle de traitement terminée")
    
    def is_running(self):
        """Retourne True si le worker est en cours d'exécution."""
        return self._is_running


# Instance globale du worker (optionnel, pour faciliter l'utilisation)
_worker_instance = None

def start_api_worker(check_interval=10,retry_interval=60):
    """Démarre le worker API global."""
    global _worker_instance
    if _worker_instance is None:
        _worker_instance = APIWorkerThread(check_interval=check_interval,retry_interval=retry_interval)
    _worker_instance.start()
    return _worker_instance

def stop_api_worker():
    """Arrête le worker API global."""
    global _worker_instance
    if _worker_instance:
        _worker_instance.stop()

def get_api_worker():
    """Retourne l'instance du worker API global."""
    return _worker_instance
