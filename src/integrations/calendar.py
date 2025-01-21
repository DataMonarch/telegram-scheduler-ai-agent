from __future__ import print_function
import datetime
import json
import os
import pickle
from collections import defaultdict

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Define the scope for Google Calendar
SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]


def authenticate_google_calendar():
    """
    Authenticate and return a Google Calendar API service object.
    """
    creds = None

    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            config_dir = "config"
            json_files = [f for f in os.listdir(config_dir) if f.endswith(".json")]
            if not json_files:
                raise FileNotFoundError("No JSON files found in config directory")
            if len(json_files) > 1:
                raise ValueError(
                    "Multiple JSON files found in config directory. Please ensure only one client secret file exists."
                )
            client_secret_file = os.path.join(config_dir, json_files[0])
            flow = InstalledAppFlow.from_client_secrets_file(
                client_secret_file,
                SCOPES,
            )
            creds = flow.run_local_server(port=0)

        with open("token.pickle", "wb") as token:
            pickle.dump(creds, token)
    return build("calendar", "v3", credentials=creds)


def get_next_week_events(service):
    """
    Retrieve events scheduled for the next week from the user's primary Google Calendar.
    """

    today = datetime.datetime.utcnow()

    days_until_monday = (7 - today.weekday()) % 7 or 7
    next_week_start = today + datetime.timedelta(days=days_until_monday)
    next_week_start = next_week_start.replace(hour=0, minute=0, second=0, microsecond=0)

    next_week_end = next_week_start + datetime.timedelta(days=7)
    next_week_end = next_week_end.replace(hour=23, minute=59, second=0, microsecond=0)

    time_min = next_week_start.isoformat() + "Z"
    time_max = next_week_end.isoformat() + "Z"

    events_result = (
        service.events()
        .list(
            calendarId="primary",
            timeMin=time_min,
            timeMax=time_max,
            singleEvents=True,
            orderBy="startTime",
        )
        .execute()
    )

    events = events_result.get("items", [])
    event_list = []
    for event in events:
        event_details = {
            "id": event.get("id"),
            "summary": event.get("summary", "No Title"),
            # Try to get the dateTime, if not available use date (all-day event)
            "start": event["start"].get("dateTime", event["start"].get("date")),
            "end": event["end"].get("dateTime", event["end"].get("date")),
            "location": event.get("location", "No Location"),
            "attendees": [
                attendee.get("email", "Unknown")
                for attendee in event.get("attendees", [])
            ],
        }
        event_list.append(event_details)

    return event_list


def format_time(iso_time):
    """
    Convert an ISO formatted time string to a formatted time string (e.g., "3:00pm").
    This function assumes the ISO string contains time information.
    """
    if iso_time.endswith("Z"):
        iso_time = iso_time[:-1]
    dt = datetime.datetime.fromisoformat(iso_time)
    return dt.strftime("%I:%M%p").lstrip("0").lower()


def build_events_by_weekday(events):
    """
    Build a dictionary grouping events by weekday (Monday-Friday) and formatting their
    time intervals as "start_time-end_time".
    """
    weekdays = defaultdict(list)
    for event in events:
        start = event["start"]
        end = event["end"]
        # Skip all-day events (which only have a date in ISO format, e.g. "2025-01-20")
        if len(start) == 10:
            continue
        start_time = format_time(start)
        end_time = format_time(end)
        time_range = f"{start_time}-{end_time}"

        # Determine the event's day using its start time
        dt = datetime.datetime.fromisoformat(start.rstrip("Z"))
        day = dt.strftime("%A")  # Returns full weekday name, e.g., "Monday"

        # Only group Monday-Friday events
        if day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]:
            weekdays[day].append(time_range)

    return weekdays
