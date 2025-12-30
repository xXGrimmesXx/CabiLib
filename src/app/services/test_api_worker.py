"""Script de test pour le worker API thread."""
import time
import json
from internet_API_thread_worker import APIRequestQueue, start_api_worker, stop_api_worker

def test_worker():
    """Teste le worker avec quelques requêtes en queue."""
    
    # Initialiser la DB
    APIRequestQueue.init_database()
    print("✓ Base de données initialisée")
    
    # Ajouter quelques requêtes de test
    print("\n=== Ajout de requêtes de test ===")
    
    # Exemple 1: Envoyer un email
    email_payload = json.dumps({
        'to': 'test@example.com',
        'subject': 'Test Email',
        'body': 'Ceci est un test'
    })
    APIRequestQueue.enqueue_api_request('gmail_send_email', email_payload)
    print("✓ Email ajouté à la queue")
    
    # Exemple 2: Créer un événement calendrier
    event_payload = json.dumps({
        'summary': 'Rendez-vous test',
        'start': '2025-12-29T10:00:00',
        'end': '2025-12-29T11:00:00'
    })
    APIRequestQueue.enqueue_api_request('calendar_create_event', event_payload)
    print("✓ Événement calendrier ajouté à la queue")
    
    # Démarrer le worker
    print("\n=== Démarrage du worker ===")
    worker = start_api_worker(check_interval=5)
    print(f"✓ Worker démarré (check tous les 5s)")
    
    # Laisser le worker tourner pendant 20 secondes
    print("\n=== Worker en cours d'exécution ===")
    print("Le worker traite les requêtes en arrière-plan...")
    print("(Attendez 20 secondes)")
    
    for i in range(20):
        time.sleep(1)
        print(".", end="", flush=True)
    
    print("\n\n=== Arrêt du worker ===")
    stop_api_worker()
    print("✓ Worker arrêté")
    
    print("\n=== Test terminé ===")
    print("Note: Les requêtes échouent normalement car les services réels")
    print("nécessitent des credentials Google. Vérifiez api_queue.db pour")
    print("voir les statuts (failed/sent).")

if __name__ == '__main__':
    test_worker()
