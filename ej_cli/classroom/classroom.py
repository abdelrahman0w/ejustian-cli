from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import os
from typing import Any, List

# Implement Google Classroom API
# https://developers.google.com/classroom/quickstart/python
# Implement the following:
# TODO: Join a Class
# TODO: Show TO-DO
# TODO: Show Classes
# TODO: Submit Assignment
# TODO: Check Grades
# TODO: Check Assignment Grade
# TODO: Show Class Materials
# TODO: Show Class Posts

SCOPES = ['https://www.googleapis.com/auth/classroom.courses.readonly']

class Classroom:
    def __init__(self) -> None:
        pass

    def join_class(self):
        """
        Join a class using the class code.
        """
        pass

    def show_todo(self):
        """
        Show student to-do.
        """
        pass

    def show_classes(self) -> List[str]:
        """
        Show current student classes.
        """
        courses : List[dict] = self.__get_courses()
        course_names : List[str] = []
        if courses:
            for course in courses:
                course_names.append(course['name'])

        return course_names

    def submit_assignment(self):
        """
        Submit an assignment.
        """
        pass

    def check_grades(self):
        """
        Check course grades.
        """
        pass

    def check_assignment_grade(self):
        """
        Check assignment grade.
        """
        pass

    def show_class_materials(self):
        """
        Show class materials.
        """
        pass

    def show_class_posts(self):
        """
        Show class posts.
        """
        pass

    def show_class_announcements(self):
        """
        Show class announcements.
        """
        pass

    def show_class_work(self):
        """
        Show class work.
        """
        pass

    """
    Private methods
    """

    def __autenticate(self) -> Any: # TODO : create a generic type for the credentials
        """
        Authenticates using OAuth2
        """
        creds = None

        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('token.json', 'w') as token:
                token.write(creds.to_json())
        return creds

    def __get_courses(self) -> List[dict]:
        """
        Get all courses that the user is enrolled in
        """
        creds = self.__autenticate()
        try:
            service = build('classroom', 'v1', credentials=creds)
            results = service.courses().list().execute()
            courses = results.get('courses', [])
        except HttpError as error:
            print('An error occurred: %s' % error)

        return courses
