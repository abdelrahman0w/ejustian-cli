from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


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

    def show_classes(self):
        """
        Show current student classes.
        """
        pass

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
