from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import os
from typing import Any, List, Tuple

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

SCOPES = [
    "https://www.googleapis.com/auth/classroom.coursework.students",
    "https://www.googleapis.com/auth/classroom.courses.readonly",
    "https://www.googleapis.com/auth/classroom.coursework.me",
    "https://www.googleapis.com/auth/classroom.student-submissions.students.readonly",
    "https://www.googleapis.com/auth/classroom.student-submissions.me.readonly",
]


class Classroom:
    def __init__(self) -> None:
        pass

    def join_class(self):
        """
        Join a class using the class code.
        """
        pass

    def show_todo(self) -> List[dict]:
        """
        Show student to-do in the first 5 courses.

        Output dic keys are {"course_name", "due_date", "title"}
        """
        creds = self.__autenticate()
        courses = self.__get_courses(5)
        service = build("classroom", "v1", credentials=creds)
        todo: List[dict[int]] = []
        for course in courses:
            course_work_response = service.courses().courseWork()
            submissions_response = (
                course_work_response.studentSubmissions()
                .list(
                    courseId=course["id"], courseWorkId="-", states=["NEW", "CREATED"]
                )
                .execute()
            )
            course_work_submissions = submissions_response.get("studentSubmissions", [])
            for course_work_submission in course_work_submissions:
                submission = {}
                submission["course_name"] = course["name"]
                course_work_obj = course_work_response.get(
                    courseId=course["id"], id=course_work_submission["courseWorkId"]
                ).execute()
                submission["due_date"] = course_work_obj["dueDate"]
                submission["title"] = course_work_obj["title"]
                todo.append(submission)
        return todo

    def show_classes(self) -> List[str]:
        """
        Show current student classes.
        """
        courses: List[dict] = self.__get_courses()
        course_names: List[str] = []
        if courses:
            for course in courses:
                course_names.append(course["name"])

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

    def show_class_announcements(self):
        pass
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

    def __autenticate(self) -> Any:  # TODO : create a generic type for the credentials
        """
        Authenticates using OAuth2
        """
        creds = None

        if os.path.exists("token.json"):
            creds = Credentials.from_authorized_user_file("token.json", SCOPES)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    "credentials.json", SCOPES
                )
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open("token.json", "w") as token:
                token.write(creds.to_json())
        return creds

    def __get_courses(self, number_of_courses: int = 0) -> List[dict]:
        """
        Get all courses that the user is enrolled in
        """
        creds = self.__autenticate()
        try:
            service = build("classroom", "v1", credentials=creds)

            results = service.courses().list(pageSize=number_of_courses).execute()
            courses = results.get("courses", [])
        except HttpError as error:
            print("An error occurred: %s" % error)

        return courses


x = Classroom()

print(x.show_todo())
