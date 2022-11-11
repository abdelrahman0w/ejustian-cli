import os
from datetime import datetime, timedelta
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from .schedule import Schedule


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(BASE_DIR)
SCOPES = ["https://www.googleapis.com/auth/calendar"]


class Calendar:
    def __init__(self, cal: Schedule) -> None:
        self.cal = cal

    def __date(self, day: str) -> str:
        day = day.lower()
        days = [
            "monday", "tuesday", "wednesday",
            "thursday", "friday", "saturday", "sunday"
        ]
        today = datetime.now()
        day_index = days.index(day)
        day_date = today + timedelta((day_index - today.weekday()) % 7)

        return day_date.strftime("%Y-%m-%d")

    @property
    def __events(self):
        def parse_time(time):
            start, end = time.split(" - ")
            s_hours, s_mins = start.split(":")
            e_hours, e_mins = end.split(":")
            s_hours = s_hours if len(s_hours) == 2 else f"0{s_hours}"
            s_mins = s_mins if len(s_mins) == 2 else f"0{s_mins}"
            e_hours = e_hours if len(e_hours) == 2 else f"0{e_hours}"
            e_mins = e_mins if len(e_mins) == 2 else f"0{e_mins}"

            return f"{s_hours}:{s_mins}:00", f"{e_hours}:{e_mins}:00"

        return [
            [
                {
                    "summary": f"{course.code} - {course.name}",
                    "location": course.venue,
                    "description": f"{course.type} - {course.instructor}",
                    "start": {
                        "dateTime": f"{self.__date(day.day)}T{parse_time(course.time)[0]}",
                        "timeZone": "Africa/Cairo"
                    },
                    "end": {
                        "dateTime": f"{self.__date(day.day)}T{parse_time(course.time)[1]}",
                        "timeZone": "Africa/Cairo"
                    },
                    "recurrence": [
                        "RRULE:FREQ=WEEKLY;COUNT=9"],
                    "reminders": {
                        "useDefault": False,
                        "overrides": [
                            {"method": "email", "minutes": 24 * 60},
                            {"method": "popup", "minutes": 10},
                        ]
                    },
                } for course in day.courses
            ]
            for day in self.cal.week_days
        ]

    @property
    def __service(self):
        creds = None
        if os.path.exists(
            os.path.join(PARENT_DIR, "saved", "token.json")
        ):
            creds = Credentials.from_authorized_user_file(
                os.path.join(PARENT_DIR, "saved", "token.json"),
                SCOPES
            )
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    os.path.join(
                        PARENT_DIR, "saved",
                        "credentials.json"
                    ), SCOPES
                )
                creds = flow.run_local_server(port=0)
            with open(
                os.path.join(PARENT_DIR, "saved", "token.json"),
                "w"
            ) as token:
                token.write(creds.to_json())

        return build("calendar", "v3", credentials=creds)

    @property
    def export(self):
        try:
            service = self.__service
            for day in self.__events:
                for event in day:
                    try:
                        service.events().insert(
                            calendarId="primary",
                            body=event
                        ).execute()
                    except HttpError as e:
                        print(e)
        except HttpError as e:
            print(e)
