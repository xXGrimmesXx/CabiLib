from datetime import datetime, timedelta,timezone
from app.services.google_api_manager import get_calendarV3_service
import app.services.constantes_manager as cm
from app.model.rendezVous import RendezVous
from app.model.patient import Patient
from app.model.typeRDV import TypeRDV

try:
  from googleapiclient.errors import HttpError
except Exception:
  HttpError = Exception

CALENDAR_ID = None

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
        content = str(e)
      print(f"HTTP error fetching events: {content}")
    else:
      print(f"Error fetching events: {e}")
    return []

  events = events_result.get("items", [])
  print(f"Fetched {len(events)} events from {time_min} to {time_max}.")
  print("\n\n", events)
  return events

def create_event(rdv:RendezVous):
  """
  Cree un rendez-vous pour google calendar
  Args :
      rdv (RendezVous) : L'objet RendezVous dont on veut créer le rendez-vous
  Return :
      event (Dict) : l'objet rendez-vous à envoyer a l'API google calendar
  """

  typerdv = TypeRDV.getTypeRDVById(rdv.type_id)
  patient = Patient.getPatientById(rdv.patient_id)
  start_date = rdv.date.isoformat()
  end_date = rdv.date + typerdv.duree
  end_date = end_date.isoformat()

  summary = f"RDV avec {patient.nom} {patient.prenom} - {typerdv.nom}"
  if (patient.adresse is None) :
    patient.adresse = "Adresse non renseignée"
  elif (patient.ville is None) :
    patient.ville = "Ville non renseignée"
  elif (patient.adresse == "") :
    patient.adresse = "Adresse non renseignée"
  elif (patient.ville == "") :
    patient.ville = "Ville non renseignée"
  elif (typerdv.localisation is not None and typerdv.localisation != "Domicile") :
    localisation = f"{patient.adresse}, {patient.ville}"
  elif (typerdv.localisation == "Cabinet") :
    localisation = cm.get_constante("CABINET_ADDRESS")

  
  description = f"id : {rdv.id}"

  event = {
      'summary': summary,
      'location': localisation,
      'description': description,
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

def modify_rdv (oldRDV:RendezVous,newRDV:RendezVous) : 
  """
  Modification d'un rendez-vous déjà dans l'agenda

  Args:
      rdv (RendezVous): L'objet RendezVous à modifier dans le calendrier.
  """
  # Ensure datetimes are timezone-aware (RFC3339). If naive, assume Europe/Paris.
  start_dt = oldRDV.date - timedelta(minutes=1)
  end_dt = oldRDV.date + TypeRDV.getTypeRDVById(oldRDV.type_id).duree + timedelta(minutes=1)
  if start_dt.tzinfo is None:
    # assume Europe/Paris as used elsewhere in create_event
    try:
      from zoneinfo import ZoneInfo
      tz = ZoneInfo("Europe/Paris")
    except Exception:
      tz = timezone.utc
    start_dt = start_dt.replace(tzinfo=tz)
  if end_dt.tzinfo is None:
    try:
      from zoneinfo import ZoneInfo
      tz = ZoneInfo("Europe/Paris")
    except Exception:
      tz = timezone.utc
    end_dt = end_dt.replace(tzinfo=tz)

  old_start_date = start_dt.isoformat()
  old_end_date = end_dt.isoformat()
  service = get_calendarV3_service()
  event = create_event(newRDV)
  global CALENDAR_ID
  if CALENDAR_ID is None :
    create_calendar_if_not_exist()
  try : 
    print("--------------------[DEBUG]--------------------")
    print(CALENDAR_ID)
    print("old_start_date:", old_start_date)
    print("old_end_date:", old_end_date)
    print("-----------------------------------------------")
    eventlist = service.events().list(calendarId=str(CALENDAR_ID), timeMin=old_start_date, timeMax=old_end_date).execute()
    print("NOMBRE d'éléments : ",len(eventlist.get('items', [])))
    for e in eventlist.get('items', []):
      print("EVENT : ",e)
      print("DESCRIPTION RDV calendar :",e.get('description', ''))
      print("DESCRIPTION RDV local   :",event["description"])
      if event["description"] in e.get('description', ''):
        event["description"] = e.get('description', '')
        print("too good avant update")
        event = service.events().update(calendarId=CALENDAR_ID, eventId=e['id'], body=event).execute()
        print('après update')
        return event
    
  except Exception as e:
    print(f"An error occurred while inserting the event: {e}")
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
  try : 
    event = service.events().insert(calendarId=CALENDAR_ID, body=event).execute()
  except Exception as e:
    print(f"An error occurred while inserting the event: {e}")
    return None
  return event

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
      continue


if __name__ == "__main__":
  create_calendar_if_not_exist()
  main()