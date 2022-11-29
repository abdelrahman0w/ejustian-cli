import os
import re
import json
from typing import Optional
import requests
from bs4 import BeautifulSoup
from tabulate import tabulate
from .regex import matches
from .schedule import Course, WeekDay, Schedule
from .gcalendar import Calendar
from .template import MD_DATA


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(BASE_DIR)


class SIS:
    def __init__(self, id: str, pwd: str) -> None:
        self.id = id
        self.pwd = pwd
        self.host = "https://sis.ejust.edu.eg"
        try:
            with open(os.path.join(PARENT_DIR, "saved", f"{self.id}-info.json")) as f:
                self.__data = json.load(f)
        except FileNotFoundError:
            self.__data = {}

    def __req(
        self,
        session: requests.Session,
        url: str,
        method: str = "GET",
        headers: Optional[dict] = None,
        data: Optional[dict] = None
    ) -> requests.Response:
        if headers:
            session.headers.update(headers)

        if method.lower() == "get":
            res = session.get(url)
        elif method.lower() == "post":
            if data:
                res = session.post(url, data=data)
            else:
                raise ValueError("data is required for POST requests")
        else:
            raise ValueError("Invalid method")

        return res

    def __authenticate(self, session: requests.Session) -> None:
        host = f"{self.host}/Default.aspx"
        login_page = self.__req(
            session=session, url=host)
        soup = BeautifulSoup(login_page.content, "lxml")
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

        self.__req(
            session=session, url=host, method="POST", data=login_data
        )

    @property
    def __get_info(self) -> None:
        with requests.Session() as crnt_session:
            self.__authenticate(session=crnt_session)

            index_res = self.__req(
                session=crnt_session,
                url=f"{self.host}/UI/StudentView/Home.aspx"
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
            if not os.path.exists(
                os.path.join(
                    PARENT_DIR,
                    "saved",
                    f"{self.id}-info.json")
            ):
                with open(
                    os.path.join(
                        PARENT_DIR,
                        "saved",
                        f"{self.id}-info.json"
                    ),
                    "w"
                ) as f:
                    json.dump(data, f, indent=4)

    @property
    def info(self) -> str:
        if not self.__data:
            self.__get_info

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

    @property
    def cgpa(self) -> str:
        if not self.__data:
            self.__get_info

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
            self.__get_info

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
    def __get_attendance(self) -> dict:
        with requests.Session() as crnt_session:
            self.__authenticate(session=crnt_session)
            attendance_res = self.__req(
                session=crnt_session,
                url=f"{self.host}/UI/StudentView/StudAttendanceFW.aspx"
            )

        return {
            "Course Code": re.findall(matches["courses_codes"], attendance_res.text),
            "Course Name": re.findall(matches["courses_names"], attendance_res.text),
            "Absence Times": re.findall(matches["absence_times"], attendance_res.text),
            "Warnings": re.findall(matches["warnings"], attendance_res.text),
        }

    @property
    def attendance(self) -> str:
        attendance_data = self.__get_attendance

        attendance_table = tabulate(
            tabular_data=attendance_data,
            headers="keys",
            tablefmt="pretty"
        )

        if len(attendance_data["Course Code"]) == 0:
            return "Whoa! You have no absences! Keep it up!\nOr maybe it's just not updated yet :/"

        return attendance_table

    @property
    def advisor(self) -> str:
        with requests.Session() as crnt_session:
            self.__authenticate(session=crnt_session)
            advisor_page = self.__req(
                session=crnt_session,
                url=f"{self.host}/UI/StudentView/Home.aspx"
            )
            soup = BeautifulSoup(advisor_page.content, "lxml")
            VIEWSTATE = soup.find(id="__VIEWSTATE")['value']
            VIEWSTATEGENERATOR = soup.find(id="__VIEWSTATEGENERATOR")['value']
            EVENTVALIDATION = soup.find(id="__EVENTVALIDATION")['value']
            data = {
                "ctl00$ScriptManager1": "ctl00$cntphmaster$StudDataGeneralControl1$StudentDtlPopup$ucStudDtlsTabsGnrlCtrl$TabHeader1$updPnlTabs|ctl00$cntphmaster$StudDataGeneralControl1$StudentDtlPopup$ucStudDtlsTabsGnrlCtrl$TabHeader1$rptTabs$ctl00$lnkTab",
                "ctl00_ASPxPopupControl1WS": "0:0:-1:-10000:-10000:0:-10000:-10000:1",
                "ctl00$FixNumericBoxProblem": "",
                "ctl00$txtFixCalendarProblem": "",
                "ctl00$MaskedBirthDate_ClientState": "",
                "ctl00$txtSearch": "",
                "ctl00$cntphmaster$StudDataGeneralControl1$txtInsertMode": False,
                "ctl00_cntphmaster_StudDataGeneralControl1_StudentDtlPopupWS": "1:1:12000:0:0:0:-10000:-10000:1",
                "ctl00$cntphmaster$StudDataGeneralControl1$StudentDtlPopup$ucStudDtlsTabsGnrlCtrl$TabHeader1$txtTabLvl": "1",
                "ctl00$cntphmaster$StudDataGeneralControl1$StudentDtlPopup$ucStudDtlsTabsGnrlCtrl$TabHeader1$Tab_UcStudentAcademicDataTabs_1$drpDegreeFac": "425",
                "ctl00$cntphmaster$StudDataGeneralControl1$StudentDtlPopup$ucStudDtlsTabsGnrlCtrl$TabHeader1$Tab_UcStudentAcademicDataTabs_1$ucTabHeader$txtTabLvl": "2",
                "ctl00_cntphmaster_StudDataGeneralControl1_StudentDtlPopup_ucStudDtlsTabsGnrlCtrl_StudentDtlPopupWS": "0:0:-1:-10000:-10000:0:999px:-10000:1",
                "ctl00_cntphmaster_StudDataGeneralControl1_StudentDtlAfcmPopupWS": "0:0:-1:-10000:-10000:0:-10000:-10000:1",
                "ctl00$cntphmaster$StudDataGeneralControl1$StudentDtlAfcmPopup$StudDtlsTabsGnrlCtrlAfcm$TabHeader1$txtTabLvl": "1",
                "ctl00$cntphmaster$StudDataGeneralControl1$StudentDtlAfcmPopup$StudDtlsTabsGnrlCtrlAfcm$TabHeader1$Tab_UcStudentBasicDataTabs_0$ucTabHeader$txtTabLvl": "2",
                "ctl00$cntphmaster$StudDataGeneralControl1$StudentDtlAfcmPopup$StudDtlsTabsGnrlCtrlAfcm$TabHeader1$Tab_UcStudentBasicDataTabs_0$ucTabHeader$Tab_StudBasicData_View_0$txtStudId": "425",
                "ctl00$cntphmaster$StudDataGeneralControl1$StudentDtlAfcmPopup$StudDtlsTabsGnrlCtrlAfcm$TabHeader1$Tab_UcStudentBasicDataTabs_0$ucTabHeader$Tab_StudBasicData_View_0$txthiddenStudID": "ED_STUD_ID=425",
                "ctl00$cntphmaster$StudDataGeneralControl1$StudentDtlAfcmPopup$StudDtlsTabsGnrlCtrlAfcm$TabHeader1$Tab_UcStudentBasicDataTabs_0$ucTabHeader$Tab_StudBasicData_View_0$UpdatedStudID": "425",
                "ctl00_cntphmaster_StudDataGeneralControl1_StudentDtlAfcmPopup_StudDtlsTabsGnrlCtrlAfcm_StudentDtlPopupWS": "0:0:-1:-10000:-10000:0:999px:-10000:1",
                "ctl00$cntphmaster$hdnid": True,
                "ctl00_cntphmaster_PopupStudPalnWS": "0:0:-1:-10000:-10000:0:850px:-10000:1",
                "ctl00$cntphmaster$PopupStudPaln$hidenval": "",
                "ctl00$cntphmaster$PopupStudPaln$txtStudCode2": "",
                "ctl00$cntphmaster$PopupStudPaln$txtStudID": "",
                "ctl00_cntphmaster_popSurveysWS": "0:0:-1:-10000:-10000:0:1000px:80%:1",
                "ctl00$cntphmaster$popSurveys$hdnchngPassUserId": "",
                "ctl00$cntphmaster$popSurveys$SurveyControl$txtEntMainId": "",
                "ctl00$cntphmaster$popSurveys$SurveyControl$txtSvStaffEvlId": "",
                "ctl00$cntphmaster$popSurveys$SurveyControl$txtSaStfMemberId": "",
                "ctl00$cntphmaster$popSurveys$SurveyControl$txtEdCourseId": "",
                "ctl00$cntphmaster$popSurveys$SurveyControl$txtEvalID": "",
                "ctl00$cntphmaster$popSurveys$SurveyControl$txtstaffId": "",
                "ctl00_cntphmaster_popSurveysDynWS": "0:0:-1:-10000:-10000:0:1000px:100%:1",
                "ctl00$cntphmaster$popSurveysDyn$SurveyControlDyn$txtEntMainId": "",
                "ctl00$cntphmaster$popSurveysDyn$SurveyControlDyn$txtSvStaffEvlId": "",
                "ctl00$cntphmaster$popSurveysDyn$SurveyControlDyn$txtSaStfMemberId": "",
                "ctl00$cntphmaster$popSurveysDyn$SurveyControlDyn$txtEdCourseId": "",
                "ctl00$cntphmaster$popSurveysDyn$SurveyControlDyn$txtstaffId": "",
                "ctl00$txthdndegreeclassctrl_Ids": "0",
                "DXScript": "1_42,1_74,1_67,1_64",
                "__EVENTTARGET": "ctl00$cntphmaster$StudDataGeneralControl1$StudentDtlPopup$ucStudDtlsTabsGnrlCtrl$TabHeader1$rptTabs$ctl01$lnkTab",
                "__EVENTARGUMENT": "",
                "__LASTFOCUS": "",
                "__VIEWSTATE": VIEWSTATE,
                "__VIEWSTATEGENERATOR": VIEWSTATEGENERATOR,
                "__EVENTVALIDATION": EVENTVALIDATION,
                "__VIEWSTATEENCRYPTED": "",
                "__ASYNCPOST": True,
            }

            advisor_res = self.__req(
                session=crnt_session,
                method="post",
                url=f"{self.host}/UI/StudentView/Home.aspx",
                data=data,
            )

            return re.findall(matches["advisor_name"], advisor_res.text)[0]

    @property
    def __get_calendar(self) -> Schedule:
        with requests.Session() as crnt_session:
            self.__authenticate(session=crnt_session)
            student_calendar = self.__req(
                session=crnt_session,
                url=f"{self.host}/UI/StudentView/StudCourseTime.aspx"
            )

        week_days = re.findall(matches["cal_week_days"], student_calendar.text)
        tmp_cal = []

        for week_day in week_days:
            crnt_day = re.findall(matches["cal_day"], week_day)[0]
            courses_codes = re.findall(matches["cal_courses_codes"], week_day)
            courses_names = re.findall(matches["cal_courses_names"], week_day)
            courses_types = re.findall(matches["cal_courses_types"], week_day)
            times = re.findall(matches["cal_times"], week_day)
            buildings = map(
                lambda x: x.replace("Building ", "B"),
                re.findall(matches["cal_buildings"], week_day)
            )
            rooms = re.findall(matches["cal_rooms"], week_day)
            instructors = re.findall(matches["cal_instructors"], week_day)
            day = WeekDay(
                day=crnt_day,
                courses=[
                    Course(
                        code=course_code,
                        name=course_name,
                        type=course_type,
                        time=time,
                        venue=f"{building} - {room}",
                        instructor=instructor,
                    ) for
                    course_code,
                    course_name,
                    course_type,
                    time,
                    building,
                    room,
                    instructor in zip(
                        courses_codes,
                        courses_names,
                        courses_types,
                        times,
                        buildings,
                        rooms,
                        instructors
                    )
                ]
            )

            tmp_cal.append(day)

        return Schedule(week_days=tmp_cal)

    @property
    def show_calendar(self):
        return tabulate(
            tabular_data=[
                [
                    day.day,
                    course.code,
                    course.name,
                    course.type,
                    course.time,
                    course.venue,
                    course.instructor,
                ] for day in self.__get_calendar.week_days for course in day.courses
            ],
            headers=[
                "Day", "Course Code", "Course Name",
                "Course Type", "Time", "Venue", "Instructor"
            ],
            tablefmt="rst"
        )

    @property
    def pdf_calendar(self) -> None:
        table = tabulate(
            tabular_data=[
                [
                    day.day,
                    course.code,
                    course.name,
                    course.type,
                    course.time,
                    course.venue,
                    course.instructor,
                ] for day in self.__get_calendar.week_days for course in day.courses
            ],
            headers=[
                "Day", "Course Code", "Course Name",
                "Course Type", "Time", "Venue", "Instructor"
            ],
            tablefmt="github"
        )
        md_data = MD_DATA
        md_data = md_data.replace("{{ID}}", self.id)
        md_data = md_data.replace("{{TABLE}}", table)
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        data = {
            'markdown': md_data,
            'engine': 'pdflatex',
        }

        with requests.Session() as crnt_session:
            res = self.__req(
                session=crnt_session, method="post",
                url="https://md-to-pdf.fly.dev",
                headers=headers,
                data=data
            )

        with open(os.path.join(os.getcwd(), f'{self.id}-schedule.pdf'), 'wb') as f:
            f.write(res.content)

    @property
    def export_calendar(self):
        cal = self.__get_calendar
        google_cal = Calendar(cal=cal)
        google_cal.export
