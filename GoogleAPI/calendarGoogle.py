import datetime
import tzlocal as tzl
import pytz
from rfc3339 import rfc3339

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from GoogleAPI.googleTokenManager import GoogleTokenManager 

class CalendarGoogle:
  def __init__(self):
    self.timeZone = str(tzl.get_localzone())
    self.tokenManager = GoogleTokenManager()

  def parseEvent(self, request):
    # Name from _ AM/PM to _ AM/PM on DATE to my schedule
    start, end = request["starttime"], request["endtime"]
    if ("PM" not in start and "AM" not in start) or ("PM" not in end and "AM" not in end):
      return "Bad Time", None, None, None
    
    name = request["event-name"]

    date = request["date"]

    if not start or not end or not date or not name:
      return None, None, None, None
    
    return start, end, date, name


  def get_service_events(self):
    creds = self.tokenManager.getCreds()
    try:
      service = build("calendar", "v3", credentials=creds)

      calendar_id = 'primary'

      now = datetime.datetime.now(pytz.timezone(self.timeZone)).isoformat()
      events_result = service.events().list(calendarId=calendar_id, timeMin=now, singleEvents=True, orderBy='startTime').execute()
      events = events_result.get('items', [])
      return service, events
    except HttpError as error:
      print(f"An error occurred: {error}")
      return None, None


  def remove(self, name):
    search_name = " ".join(name).lower()
    try:
      service, events = self.get_service_events()
      if not service or not events:
        return

      if not events:
        print('No upcoming events found.')
        return

      for event in events:
        if event['summary'].lower() == search_name:
          event_id = event['id']
          print(f"Deleting event: {event['summary']} ({event_id})")
          service.events().delete(calendarId='primary', eventId=event_id).execute()
          print("Event deleted successfully.")
          return 

      print(f"Event with name '{name}' not found.")

    except HttpError as error:
      print(f"An error occurred: {error}")

  def add(self, start, end, date, name):
    startTime = self.time_formatted(start, date)
    endTime = self.time_formatted(end, date)

    event = {
      'summary': name,
      'start': [{
        'dateTime': startTime,
        'timeZone': self.timeZone,
      }],
      'end': [{
        'dateTime': endTime,
        'timeZone': self.timeZone,
      }],
    }
    service, events = self.get_service_events()
    event = service.events().insert(calendarId='primary', body=event).execute()
    print("Successfully added item")

  def time_formatted(self, time, date):
    hour = int(time[:time.index(":")])
    minutes = int(time[time.index(":")+1:len(time)-2])
    if("PM" in time):
      hour+=12
    
    format_code = "%Y-%m-%d"
    date_obj = datetime.datetime.strptime(date, format_code).date()
    day = int(date_obj.day)
    month = int(date_obj.month)
    year = int(date_obj.year)

    final_date = datetime.datetime(year, month, day, hour, minutes)
    return rfc3339(final_date, utc=True, use_system_timezone=True)

def main():
  """
  Shows basic usage of the Google Calendar API.
  Prints the start and name of the next 10 events on the user's calendar.
  """
  test = CalendarGoogle()
  creds = test.tokenManager.getCreds()

  try:
    service = build("calendar", "v3", credentials=creds)

    # Call the Calendar API
    now = datetime.datetime.now().isoformat() + "Z"  # 'Z' indicates UTC time
    print("Getting the upcoming 10 events")
    events_result = (
        service.events()
        .list(
            calendarId="primary",
            timeMin=now,
            maxResults=10,
            singleEvents=True,
            orderBy="startTime",
        )
        .execute()
    )
    events = events_result.get("items", [])

    if not events:
      print("No upcoming events found.")
      return
    
    pst_timezone = pytz.timezone(test.timeZone)  # Define the PST timezone
    # Prints the start and name of the next 10 events
    for event in events:
      start = event["start"].get("dateTime", event["start"].get("date"))
      start_utc = datetime.datetime.fromisoformat(start.replace('Z', '+00:00'))  # Convert UTC string to datetime object
      start_pst = start_utc.astimezone(pst_timezone)
      print(f"{event['summary']} ({start_pst.strftime('%Y-%m-%d %I:%M %p')})")

  except HttpError as error:
    print(f"An error occurred: {error}")

# if __name__ == "__main__":
#   classi = Classifier("jarvis")
#   CalendarGoogle = CalendarGoogle()
#   request = classi.get_classification("jack's birthday break from 8:00 a.m. to 10:00 p.m. today")
#   start, end, date, name = CalendarGoogle.parseEvent(request=request)
#   CalendarGoogle.add(start, end, date, name)