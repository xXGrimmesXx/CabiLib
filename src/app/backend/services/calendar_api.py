from datetime import datetime, timedelta,timezone
import traceback
from app.backend.services.google_api_manager import get_calendarV3_service
import app.backend.services.constantes_manager as cm
from app.backend.model.rendezVous import RendezVous
from app.backend.model.typeRDV import TypeRDV

from app.backend.services.patient_service import PatientService
from app.backend.services.typeRDV_service import TypeRDVService
from app.backend.services.rendezVous_service import RendezVousService


try:
  from googleapiclient.errors import HttpError
except Exception:
  HttpError = Exception

CALENDAR_ID = None
COLORS = {
  "1": "#a4bdfc",
  "2": "#7ae7bf",
  "3": "#dbadff",
  "4": "#ff887c",
  "5": "#fbd75b",
  "6": "#ffb878",
  "7": "#46d6db",
  "8": "#e1e1e1",
  "9": "#5484ed",
  "10": "#51b749",
  "11": "#dc2127"
}

def get_color_for_type_rdv(type: TypeRDV) -> str:
  """Retourne la couleur associée à un type de rendez-vous.

  Args:
    type: L'objet TypeRDV.
  Returns:
    Une chaîne de caractères représentant la couleur hexadécimale associée au type de rendez-vous.
  """
  dist = [distance_to_color(COLORS[str(i)], type.couleur) for i in range(1, 12)]
  min_dist_index = dist.index(min(dist))
  return str(min_dist_index+1)



def distance_to_color(col1 :str, col2 :str) -> int:
  """Retourne la distance entre deux couleurs hexadécimales.

  Args:
    col1: Une chaîne de caractères représentant la première couleur hexadécimale.
    col2: Une chaîne de caractères représentant la deuxième couleur hexadécimale.
  Returns:
    Un entier représentant la distance entre les deux couleurs.
  """
  r1, g1, b1 = int(col1[1:3], 16), int(col1[3:5], 16), int(col1[5:7], 16)
  r2, g2, b2 = int(col2[1:3], 16), int(col2[3:5], 16), int(col2[5:7], 16)
  return ((r1 - r2) ** 2 + (g1 - g2) ** 2 + (b1 - b2) ** 2) ** 0.5


def create_calendar_if_not_exist ():
  """Creates a Google Calendar if it does not already exist.

  Returns:
    The ID of the created or existing calendar.
  """
  global CALENDAR_ID
  service = get_calendarV3_service()

  # Define the calendar properties
  calendar = {
      "summary": "RDV CabiLib",
      "description": "Agenda interne à l'application CabiLib pour la gestion des RDV",
      "timeZone": "Europe/Paris",
      "selected": True,
  }

  # Check if the calendar already exists
  calendar_list = service.calendarList().list().execute()
  for cal in calendar_list.get("items", []):
    if cal["summary"] == calendar["summary"]:
      CALENDAR_ID = cal["id"]
      print("Calendar already exists with ID: %s" % CALENDAR_ID)
      return CALENDAR_ID

  # Create the calendar if it does not exist
  try : 
    created_calendar = service.calendars().insert(body=calendar).execute()
    CALENDAR_ID = created_calendar["id"]
    print("Calendar created with ID: %s" % CALENDAR_ID)
    return CALENDAR_ID
  except Exception as e:
    print("An error occurred while creating the calendar: %s" % e)
    traceback.print_exc()
    return None

def get_event_by_plage(start_datetime, end_datetime):
  """Fetches events from Google Calendar within a specified time range.

  Args:
    start_datetime: A datetime object representing the start of the time range.
    end_datetime: A datetime object representing the end of the time range.
  Returns:
    A list of events within the specified time range.
  """
  global CALENDAR_ID
  service = get_calendarV3_service()

  # Ensure we have a calendar id
  if not CALENDAR_ID:
    CALENDAR_ID = create_calendar_if_not_exist()
    if not CALENDAR_ID:
      raise ValueError("Aucun CALENDAR_ID disponible — échec de création/lecture du calendrier")

  # Convert datetime objects to RFC3339 strings (timezone-aware). If naive, treat as UTC.
  if start_datetime.tzinfo is None:
    start_datetime = start_datetime.replace(tzinfo=timezone.utc)
  if end_datetime.tzinfo is None:
    end_datetime = end_datetime.replace(tzinfo=timezone.utc)

  time_min = start_datetime.isoformat()
  time_max = end_datetime.isoformat()

  # Call the Calendar API to fetch events within the specified time range
  try:
    events_result = (
        service.events()
        .list(
            calendarId=str(CALENDAR_ID),
            timeMin=time_min,
            timeMax=time_max,
            singleEvents=True,
            orderBy="startTime",
        )
        .execute()
    )
  except Exception as e:
    if isinstance(e, HttpError):
      try:
        content = e.content.decode() if hasattr(e, "content") else str(e)
      except Exception:
        traceback.print_exc()
        content = str(e)
      print(f"HTTP error fetching events: {content}")
    else:
      print(f"Error fetching events: {e}")
    traceback.print_exc()
    return []

  events = events_result.get("items", [])
  return events

def create_event(rdv:RendezVous):
  """
  Cree un rendez-vous pour google calendar
  Args :
      rdv (RendezVous) : L'objet RendezVous dont on veut créer le rendez-vous
  Return :
      event (Dict) : l'objet rendez-vous à envoyer a l'API google calendar
  """

  typerdv = TypeRDVService.get_type_by_id(rdv.type_id)
  patient = PatientService.get_patient_by_id(rdv.patient_id)
  start_date = rdv.date.isoformat()
  end_date = rdv.date + typerdv.duree
  end_date = end_date.isoformat()

  summary = f"RDV avec {patient.nom} {patient.prenom} - {typerdv.nom}"
  type_localisation = typerdv.localisation.upper() if typerdv.localisation else ""
  if ("DOMICILE" in type_localisation):
      localisation = patient.adresse_complete()
  elif ("CABINET" in type_localisation):
      localisation = cm.get_constante("CABINET_ADDRESS")
  else:
      localisation = typerdv.localisation if typerdv.localisation else ""
  description = f"{rdv.motif}\nid : {rdv.id}"
  event = {
      'summary': summary,
      'location': localisation,
      'description': description,
      'colorId': get_color_for_type_rdv(typerdv),
      'start': {
          'dateTime': start_date,
          'timeZone': 'Europe/Paris',
      },
      'end': {
          'dateTime': end_date,
          'timeZone': 'Europe/Paris',
      },
      'reminders': {
          'useDefault': True,
      },
  }
  return event

def modify_rdv (rdv:RendezVous) : 
  """
  Modification d'un rendez-vous déjà dans l'agenda

  Args:
      rdv (RendezVous): L'objet RendezVous à modifier dans le calendrier.
  """
  service = get_calendarV3_service()
  event = create_event(rdv)
  global CALENDAR_ID
  if CALENDAR_ID is None :
    create_calendar_if_not_exist()
  try : 
    if (rdv.google_calendar_id is not None) and (rdv.google_calendar_id != "") :
      event = service.events().update(calendarId=CALENDAR_ID, eventId=rdv.google_calendar_id, body=event).execute()
    return event
    
  except Exception as e:
    print(f"An error occurred while inserting the event: {e}")
    traceback.print_exc()
    return None
  return None

def insert_rdv (rdv:RendezVous) : 
  """
  Insère un rendez-vous dans le calendrier Google.
  
  Args:
      rdv (RendezVous): L'objet RendezVous à insérer dans le calendrier.
  Returns:
      dict: L'événement créé dans le calendrier.
  """
  service = get_calendarV3_service()
  event = create_event(rdv)
  global CALENDAR_ID
  if CALENDAR_ID is None :
    create_calendar_if_not_exist()
  try : 
    event = service.events().insert(calendarId=CALENDAR_ID, body=event).execute()
    rdv.google_calendar_id = event.get('id')
    RendezVousService.update_rendezvous(rdv.id,rdv)
  except Exception as e:
    print(f"An error occurred while inserting the event: {e}")
    traceback.print_exc()
    return None
  return event

def delete_rdv (rdv:RendezVous) :
  """
  Supprime un rendez-vous du calendrier Google.
  
  Args:
      rdv (RendezVous): L'objet RendezVous à supprimer du calendrier.
  """
  service = get_calendarV3_service()
  global CALENDAR_ID
  if CALENDAR_ID is None :
    create_calendar_if_not_exist()
  try : 
    if (rdv.google_calendar_id is not None) and (rdv.google_calendar_id != "") :
      service.events().delete(calendarId=CALENDAR_ID, eventId=rdv.google_calendar_id).execute()
      print(f"Rendez-vous supprimé avec l'ID : {rdv.google_calendar_id}")
  except Exception as e:
    print(f"An error occurred while deleting the event: {e}")
    traceback.print_exc()
    return None
  return None


def main():
  """Shows basic usage of the Google Calendar API.
  Prints the start and name of the next 10 events on the user's calendar.
  """
  get_event_by_plage(
      datetime.now() - timedelta(days=1),
      datetime.now() + timedelta(days=20)
  )
  rdvs = RendezVous.getAllRendezVous()
  for rdv in rdvs:
    try :
      insert_rdv(rdv)
    except Exception as e :
      print(f"[ERREUR] {e}")
      traceback.print_exc()
      continue


if __name__ == "__main__":
  create_calendar_if_not_exist()
  main()