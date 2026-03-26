class CabiLibException(Exception):
    """
    Classe de base pour toutes les exceptions personnalisées de l'application CabiLib.
    Cela permet au Frontend d'attraper n'importe quelle erreur interne avec 'except CabiLibException as e:'.
    """
    pass

class RegleMetierException(CabiLibException):
    """
    Levée lorsqu'une validation métier échoue.
    Exemple : "Le prix du rendez-vous ne peut pas être négatif."
    """
    pass

class EntiteIntrouvableException(CabiLibException):
    """
    Levée lorsqu'on cherche un élément (Patient, Facture) qui n'existe pas en base.
    Exemple : "La facture FAC-2023-10-001 est introuvable."
    """
    pass

class ConflitHoraireException(RegleMetierException):
    """
    Levée spécifiquement lorsqu'un rendez-vous chevauche un autre rendez-vous non groupé.
    """
    pass

class DatabaseException(CabiLibException):
    """
    Levée lors d'un problème technique avec la base de données SQLite/SQLAlchemy.
    """
    pass

class GoogleCalendarException(CabiLibException):
    """
    Levée lors d'un problème de synchronisation avec l'API Google Calendar.
    """
    pass
