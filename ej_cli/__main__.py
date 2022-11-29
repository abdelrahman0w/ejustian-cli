import os
import json
import inquirer
from typing import Union
import time

from .auth.user import User
from .kanban.kanban import start_kanban
from .loader.loader import Loader
from .map.map import MAP
from .sis.sis import SIS


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(BASE_DIR)


class EJUSTIAN:
    def __init__(self) -> None:
        self.__welcome
        self.__delete_older_than(30)
        self.__main_menu

    @property
    def __first_use(self) -> bool:
        return not os.path.exists(os.path.join(BASE_DIR, "saved", "USED"))

    @property
    def __used(self) -> None:
        if not self.__first_use:
            return

        with open(os.path.join(BASE_DIR, "saved", "USED"), "w"):
            pass

        print("It seems like this is your first time using EJUSTIAN CLI.")
        print("Some services might need an active internet connection.")
        print("Currently we use SIS credentials for authentication.")
        print("You have to be an EJUSTIAN to be able to use all features.")
        print("So, some options will ask for your SIS credentials.")
        print("Note: If saved, your credentials are stored locally and are only used to log you in to SIS.")
        print("They are never sent to any third party.\n")

    def __auth_ejustian(self, uid: str, pwd: str) -> None:
        user = User(uid, pwd).auth

        try:
            wifi_list = user.wifi_list
            gcp_creds = user.gcp_creds

            with open(os.path.join(BASE_DIR, "saved", "credentials.json"), "w") as f:
                json.dump(
                    gcp_creds,
                    f,
                    indent=4
                )

            with open(os.path.join(BASE_DIR, "saved", "wifi.json"), "w") as f:
                json.dump(
                    wifi_list,
                    f,
                    indent=4
                )
        except Exception as e:
            print(e)

    @staticmethod
    def __delete_older_than(days: int) -> None:
        saved_files = os.listdir(os.path.join(BASE_DIR, "saved"))

        for file in saved_files:
            if not file.endswith("-info.json"):
                continue

            file_path = os.path.join(os.path.join(BASE_DIR, "saved", file))

            if os.path.getmtime(file_path) < (time.time() - (days * 86400)):
                os.remove(file_path)

    @property
    def __get_credentials(self) -> Union[dict, None]:
        credentials_questions = [
            inquirer.Text("id", message="Please Enter Your ID"),
            inquirer.Password("pwd", message="Please Enter Your SIS Password"),
            inquirer.Confirm(
                "save", message="Save Your Credentials for Future Use?", default=True),
        ]
        credentials_ans = inquirer.prompt(credentials_questions)

        try:
            with Loader(
                "Please wait while setting things up...",
                "Thanks for waiting!"
            ):
                self.__auth_ejustian(
                    credentials_ans["id"], credentials_ans["pwd"]
                )

                if credentials_ans["save"]:
                    credentials_path = os.path.join(
                        BASE_DIR,
                        "saved",
                        f"{credentials_ans['id']}-credentials.json"
                    )

                    with open(credentials_path, "w") as f:
                        json.dump(
                            {
                                "id": credentials_ans['id'],
                                "pwd": credentials_ans['pwd']
                            },
                            f,
                            indent=4
                        )

            return credentials_ans
        except Exception as e:
            print(e)

            try_again = [
                inquirer.Confirm(
                    "try_again", message="Try Again?", default=True
                )
            ]

            if inquirer.prompt(try_again)["try_again"]:
                self.__get_credentials
            else:
                exit()

    @property
    def __reset(self):
        saved_files = os.listdir(os.path.join(BASE_DIR, "saved"))
        exclude = ["__init__.py", ".gitkeep",
                   "wifi.json", "credentials.json"]

        for file in saved_files:
            if file in exclude:
                continue

            file_path = os.path.join(os.path.join(BASE_DIR, "saved", file))

            if os.path.isfile(file_path):
                os.remove(file_path)

    @property
    def __welcome(self) -> None:
        print(
            """
            \r███████╗     ██╗██╗   ██╗ ██████╗████████╗██╗ █████╗ ███╗  ██╗
            \r██╔════╝     ██║██║   ██║██╔════╝╚══██╔══╝██║██╔══██╗████╗ ██║
            \r█████╗       ██║██║   ██║╚█████╗    ██║   ██║███████║██╔██╗██║
            \r██╔══╝  ██╗  ██║██║   ██║ ╚═══██╗   ██║   ██║██╔══██║██║╚████║
            \r███████╗╚█████╔╝╚██████╔╝██████╔╝   ██║   ██║██║  ██║██║ ╚███║
            \r╚══════╝ ╚════╝  ╚═════╝ ╚═════╝    ╚═╝   ╚═╝╚═╝  ╚═╝╚═╝  ╚══╝
            \r                     █████╗ ██╗     ██╗
            \r                    ██╔══██╗██║     ██║
            \r                    ██║  ╚═╝██║     ██║
            \r                    ██║  ██╗██║     ██║
            \r                    ╚█████╔╝███████╗██║
            \r                     ╚════╝ ╚══════╝╚═╝
            """
        )
        print("Welcome to EJUSTIAN CLI!")
        print("The command line interface app that allows EJUST students to manage all their stuff\n")

        self.__used

    @property
    def __student(self) -> Union[SIS, None]:
        id_list = [
            file.split("-")[0]
            for file in os.listdir(os.path.join(BASE_DIR, "saved"))
            if file.endswith("-credentials.json")
        ]
        id_list.extend(["Use a New ID", "Back"])
        id_menu = [
            inquirer.List(
                'ids',
                message="Which ID do you want to use?",
                choices=id_list
            )
        ]
        id_choice = inquirer.prompt(id_menu)["ids"]

        if id_choice == "Back":
            return

        if id_choice == "Use a New ID":
            user_creds = self.__get_credentials
        else:
            with open(
                os.path.join(
                    BASE_DIR, "saved", f"{id_choice}-credentials.json"
                ), "r"
            ) as f:
                user_creds = json.load(f)

            pwd_changed = [
                inquirer.Confirm(
                    "pwd_changed", message="Did You Change Your Password?", default=False
                )
            ]

            if inquirer.prompt(pwd_changed)["pwd_changed"]:
                os.remove(
                    os.path.join(
                        BASE_DIR, "saved", f"{id_choice}-credentials.json"
                    )
                )

                user_creds = self.__get_credentials

        if user_creds:
            return SIS(user_creds["id"], user_creds["pwd"])

    @property
    def __main_menu(self) -> None:
        menu = [
            inquirer.List(
                "main",
                message="What do you want to do?",
                choices=[
                    "Academic Stuff",
                    "Personal Stuff",
                    "EJUST Map",
                    "Connect to Nearest WiFi",
                    "Reset Everything",
                    "Exit"
                ],
                default="Academic Stuff"
            ),
        ]

        while True:
            choice = inquirer.prompt(menu)["main"]

            if choice == "Academic Stuff":
                self.__academic_menu
            elif choice == "Personal Stuff":
                self.__personal_menu
            elif choice == "EJUST Map":
                self.__ejust_map
            elif choice == "Connect to Nearest WiFi":
                self.__wifi
            elif choice == "Reset Everything":
                print("This will delete all your saved credentials and data.")
                reset = [
                    inquirer.Confirm(
                        "reset", message="Do You Want to Continue?", default=False
                    )
                ]

                if inquirer.prompt(reset)["reset"]:
                    with Loader("Resetting...", "Done!\nPlease restart the app"):
                        self.__reset
                        exit()
            elif choice == "Exit":
                print("Thank you for using EJUSTIAN CLI!")
                print("Bye!\n")
                exit()

    @property
    def __academic_menu(self) -> None:
        menu = [
            inquirer.List(
                "academic",
                message="What do you want to do?",
                choices=[
                    "Academic Information",
                    "Attendance Tracker",
                    "Student Schedule",
                    "Main Menu",
                    "Exit"
                ],
                default="Academic Information"
            ),
        ]

        while True:
            choice = inquirer.prompt(menu)["academic"]

            if choice == "Academic Information":
                self.__info_menu
            elif choice == "Attendance Tracker":
                if student := self.__student:
                    with Loader(
                        "\033[92m" + "Please wait while getting your data...",
                        "Thanks for waiting!"
                    ):
                        print("\n\n" + "\033[0m" + student.attendance + "\n")
            elif choice == "Student Schedule":
                self.__schedule_menu
            elif choice == "Main Menu":
                self.__main_menu
                break
            elif choice == "Exit":
                print("Thank you for using EJUSTIAN CLI!")
                print("Bye!\n")
                exit()

    @property
    def __info_menu(self):
        menu = [
            inquirer.List(
                "info",
                message="What do you want to do?",
                choices=[
                    "Your SIS Info (excluding your CGPA, GPA, Passed CH, and Remaining CH)",
                    "Your CGPA",
                    "Your Credit Hours (Passed CH, Remaining CH)",
                    "Your Academic Advisor",
                    "Back to Previous Menu",
                    "Main Menu",
                    "Exit"
                ],
                default="Your SIS Info (excluding your CGPA, GPA, Passed CH, and Remaining CH)"
            ),
        ]

        while True:
            choice = inquirer.prompt(menu)["info"]

            if choice == "Your SIS Info (excluding your CGPA, GPA, Passed CH, and Remaining CH)":
                if student := self.__student:
                    with Loader(
                        "\033[92m" + "Please wait while getting your data...",
                        "Thanks for waiting!"
                    ):
                        print("\n\n" + "\033[0m" + student.info + "\n")
            elif choice == "Your CGPA":
                if student := self.__student:
                    with Loader(
                        "\033[92m" + "Please wait while getting your data...",
                        "Thanks for waiting!"
                    ):
                        print("\n\n" + "\033[0m" + student.cgpa + "\n")
            elif choice == "Your Credit Hours (Passed CH, Remaining CH)":
                if student := self.__student:
                    with Loader(
                        "\033[92m" + "Please wait while getting your data...",
                        "Thanks for waiting!"
                    ):
                        print("\n\n" + "\033[0m" + student.credit_hours + "\n")
            elif choice == "Your Academic Advisor":
                if student := self.__student:
                    with Loader(
                        "\033[92m" + "Please wait while getting your data...",
                        "Thanks for waiting!"
                    ):
                        print("\n\n" + "\033[0m" + student.advisor + "\n")
            elif choice == "Back to Previous Menu":
                self.__academic_menu
                break
            elif choice == "Main Menu":
                self.__main_menu
                break
            elif choice == "Exit":
                print("Thank you for using EJUSTIAN CLI!")
                print("Bye!\n")
                exit()

    @property
    def __schedule_menu(self):
        menu = [
            inquirer.List(
                "schedule",
                message="What do you want to do?",
                choices=[
                    "Show Schedule",
                    "Export Schedule to PDF",
                    "Export Schedule to Your Google Calendar",
                    "Back to Previous Menu",
                    "Main Menu",
                    "Exit"
                ],
                default="Show Schedule"
            ),
        ]

        while True:
            choice = inquirer.prompt(menu)["schedule"]

            if choice == "Show Schedule":
                if student := self.__student:
                    with Loader(
                        "\033[92m" + "Please wait while getting your data...",
                        "Thanks for waiting!"
                    ):
                        print("\n\n" + "\033[0m" +
                              student.show_calendar + "\n")
            elif choice == "Export Schedule to PDF":
                if student := self.__student:
                    with Loader(
                        "\033[92m" +
                            "Please wait while exporting your calendar...",
                        "Thanks for waiting!"
                    ):
                        student.pdf_calendar

                        print(
                            "\033[92m" +
                            f"\nYour schedule has been exported to {os.getcwd()}" +
                            "\033[0m"
                        )
            elif choice == "Export Schedule to Your Google Calendar":
                if student := self.__student:
                    with Loader(
                        "\033[92m" +
                            "Please wait while exporting your calendar...",
                        "Thanks for waiting!"
                    ):
                        student.export_calendar

                        print(
                            "\033[92m" +
                            "Your schedule has been exported to your Google Calendar" +
                            "\033[0m"
                        )
            elif choice == "Back to Previous Menu":
                self.__academic_menu
                break
            elif choice == "Main Menu":
                self.__main_menu
                break
            elif choice == "Exit":
                print("Thank you for using EJUSTIAN CLI!")
                print("Bye!\n")
                exit()

    @property
    def __personal_menu(self):
        menu = [
            inquirer.List(
                "personal",
                message="What do you want to do?",
                choices=[
                    "Task Manager (Kanban Style)",
                    "Personal Attendance Tracker",
                    "Main Menu",
                    "Exit",
                ],
                default="Task Manager (Kanban Style)"
            ),
        ]

        while True:
            choice = inquirer.prompt(menu)["personal"]

            if choice == "Task Manager (Kanban Style)":
                self.__task_manager
            elif choice == "Personal Attendance Tracker":
                self.__personal_attendance
            elif choice == "Main Menu":
                self.__main_menu
                break
            elif choice == "Exit":
                print("Thank you for using EJUSTIAN CLI!")
                print("Bye!\n")
                exit()

    @property
    def __wifi(self) -> None:
        print("Coming Soon!\n")

    @property
    def __ejust_map(self) -> None:
        print(MAP)

    @property
    def __task_manager(self) -> None:
        start_kanban()

    @property
    def __personal_attendance(self) -> None:
        print("Coming Soon!\n")

    @property
    def chek_for_updates(self) -> None:
        pass


def main() -> EJUSTIAN:
    return EJUSTIAN()


if __name__ == "__main__":
    main()
