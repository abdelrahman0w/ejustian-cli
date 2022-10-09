from email import header
import os
import re
import json
from typing import Optional
import requests
from bs4 import BeautifulSoup
from tabulate import tabulate
from .regex import matches


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(BASE_DIR)


class SIS:
    def __init__(self, id: str, pwd: str, save_credentials: bool = True, new_pwd: bool = False) -> None:
        self.id = id
        self.pwd = pwd
        self.save_credentials = save_credentials
        self.__data = {}
        self.__session = None
        self.__authenticated = False

        if new_pwd and os.path.exists(
            os.path.join(PARENT_DIR, f"saved/{self.id}-credentials.json")
        ):
            os.remove(os.path.join(
                PARENT_DIR, f"saved/{self.id}-credentials.json"))

        if self.save_credentials and not os.path.exists(
            os.path.join(PARENT_DIR, f"saved/{self.id}-credentials.json")
        ):
            with open(
                os.path.join(
                    PARENT_DIR, f"saved/{self.id}-credentials.json"
                ), "w"
            ) as f:
                json.dump({"id": id, "pwd": pwd}, f, indent=4)

    def open_session(self) -> requests.Session:
        if not self.__session:
            self.__session = requests.Session()

        return self.__session

    def close_session(self, req: requests.Session) -> None:
        req.close()
        self.session = None

    def authenticate(self) -> None:
        if self.__authenticated:
            return

        if not self.__session:
            self.open_session()

        login_page = self.req("https://sis.ejust.edu.eg/Default.aspx")
        soup = BeautifulSoup(login_page.content, features="html5lib")
        VIEWSTATE = soup.find(id="__VIEWSTATE")["value"]
        VIEWSTATEGENERATOR = soup.find(id="__VIEWSTATEGENERATOR")["value"]
        EVENTVALIDATION = soup.find(id="__EVENTVALIDATION")["value"]
        login_data = {
            "__EVENTTARGET": "",
            "__EVENTARGUMENT": "",
            "__VIEWSTATE": VIEWSTATE,
            "__VIEWSTATEGENERATOR": VIEWSTATEGENERATOR,
            "__EVENTVALIDATION": EVENTVALIDATION,
            "txtUsername": self.id,
            "txtPassword": self.pwd,
            "btnEnter": "Log In"
        }
        self.req(
            "https://sis.ejust.edu.eg/Default.aspx", method="POST", data=login_data
        )

        self.__authenticated = True

    def req(
        self,
        url: str,
        method: str = "GET",
        headers: Optional[dict] = None,
        data: Optional[dict] = None
    ) -> requests.Response:
        if not self.__session:
            self.__session = self.open_session()

        if headers:
            self.__session.headers.update(headers)

        if method.lower() == "get":
            res = self.__session.get(url)
        elif method.lower() == "post":
            if data:
                res = self.__session.post(url, data=data)
            else:
                raise ValueError("data is required for POST requests")
        else:
            raise ValueError("Invalid method")

        return res

    @property
    def info(self) -> str:
        if not self.__data:
            self.__get_info()

        return tabulate(
            [
                ["Student Name", self.__data["student_name"]],
                ["Student ID", self.__data["student_id"]],
                ["Faculty", self.__data["faculty"]],
                ["Admission Year", self.__data["admission_year"]],
                ["Gender", self.__data["gender"]],
                ["Nationality", self.__data["nationality"]],
                ["National ID", self.__data["national_id"]],
                ["Birth Date", self.__data["birth_date"]],
                ["Email", self.__data["email"]],
                ["Mobile", self.__data["mobile"]],
                ["Degree", self.__data["degree"]],
                ["Student Major", self.__data["student_major"]],
                ["Level", self.__data["level"]],
                ["Enrollment Status", self.__data["enrollment_status"]],
                ["Academic Status", self.__data["academic_status"]],
                ["Passed CH",
                    "HIDDEN FOR PRIVACY (You can show it using its own command)"],
                ["Remaining CH",
                    "HIDDEN FOR PRIVACY (You can show it using its own command)"],
                ["CGPA",
                    "HIDDEN FOR PRIVACY (You can show it using its own command)"],
            ],
            tablefmt="rst",
        )

    def __get_info(self) -> None:
        try:
            with open(os.path.join(PARENT_DIR, f"saved/{self.id}-info.json")) as f:
                self.__data = json.load(f)
        except FileNotFoundError:
            if not self.__authenticated:
                self.authenticate()

            index_res = self.req(
                "https://sis.ejust.edu.eg/UI/StudentView/Home.aspx"
            )
            data = {
                "student_name": re.findall(matches["student_name"], index_res.text)[0],
                "student_id": re.findall(matches["student_id"], index_res.text)[0],
                "faculty": re.findall(matches["faculty"], index_res.text)[0],
                "admission_year": re.findall(matches["admission_year"], index_res.text)[0],
                "current_semester": re.findall(matches["current_semester"], index_res.text)[0],
                "gender": re.findall(matches["gender"], index_res.text)[0],
                "nationality": re.findall(matches["nationality"], index_res.text)[0],
                "national_id": re.findall(matches["national_id"], index_res.text)[0],
                "birth_date": re.findall(matches["birth_date"], index_res.text)[0],
                "email": re.findall(matches["email"], index_res.text)[0],
                "mobile": re.findall(matches["mobile"], index_res.text)[0],
                "degree": re.findall(matches["degree"], index_res.text)[0],
                "student_major": re.findall(matches["student_major"], index_res.text)[0],
                "level": re.findall(matches["level"], index_res.text)[0],
                "enrollment_status": re.findall(matches["enrollment_status"], index_res.text)[0],
                "academic_status": re.findall(matches["academic_status"], index_res.text)[0],
                "passed_ch": re.findall(matches["passed_ch"], index_res.text)[0]
                if re.findall(matches["passed_ch"], index_res.text) else "0",
                "remaining_ch": 160 - float(re.findall(matches["passed_ch"], index_res.text)[0])
                if re.findall(matches["passed_ch"], index_res.text) else "160",
                "cgpa": re.findall(matches["cgpa"], index_res.text)[0]
                if re.findall(matches["cgpa"], index_res.text) else "0",
                "notifications": re.findall(matches["notifications"], index_res.text),
            }

            self.__data = data
            if self.save_credentials:
                self.save

    @property
    def cgpa(self) -> str:
        if not self.__data:
            self.__get_info()

        return tabulate(
            [
                ["Student Name", self.__data["student_name"]],
                ["Student ID", self.__data["student_id"]],
                ["CGPA", self.__data["cgpa"]],
            ],
            tablefmt="rst",
        )

    @property
    def credit_hours(self) -> str:
        if not self.__data:
            self.__get_info()

        return tabulate(
            [
                ["Student Name", self.__data["student_name"]],
                ["Student ID", self.__data["student_id"]],
                ["Passed CH", self.__data["passed_ch"]],
                ["Remaining CH", self.__data["remaining_ch"]],
            ],
            tablefmt="rst",
        )

    @property
    def attendance(self) -> str:
        attendance_data = self.__get_attendance()

        attendance_table = tabulate(
            tabular_data=attendance_data,
            headers="keys",
            tablefmt="pretty"
        )

        if len(attendance_data["Course Code"]) == 0:
            return "Whoa! You have no absences! Keep it up!\nOr maybe it's just not updated yet :/"

        return attendance_table

    def __get_attendance(self):
        if not self.__authenticated:
            self.authenticate()

        attendance_res = self.req(
            "https://sis.ejust.edu.eg/UI/StudentView/StudAttendanceFW.aspx"
        )

        return {
            "Course Code": re.findall(matches["courses_codes"], attendance_res.text),
            "Course Name": re.findall(matches["courses_names"], attendance_res.text),
            "Absence Times": re.findall(matches["absence_times"], attendance_res.text),
            "Warnings": re.findall(matches["warnings"], attendance_res.text),
        }

    def advisor(self):
        # TODO: Implement this
        pass

    # TODO: Refactor save to accept file name
    @property
    def save(self):
        if not os.path.exists(f"{PARENT_DIR}/saved/{self.id}-info.json"):
            with open(f"{PARENT_DIR}/saved/{self.id}-info.json", "w") as f:
                json.dump(self.__data, f, indent=4)
