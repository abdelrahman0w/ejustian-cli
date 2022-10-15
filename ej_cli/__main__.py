import os
import json
import inquirer
from typing import Union
from .sis.sis import SIS
from .map.map import MAP
from .loader.loader import Loader
from .kanban.kanban import start_kanban


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(BASE_DIR)
FIRST_USE = next(
    (
        False for file in os.listdir(os.path.join(BASE_DIR, "saved"))
        if file.endswith("-credentials.json")
    ),
    True
)


def welcome() -> None:
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


def get_credentials(pwd_changed: bool = False):
    if pwd_changed:
        credentials_questions = [
            inquirer.Password(
                "pwd", message="Please Enter Your New SIS Password")
        ]
        credentials_ans = inquirer.prompt(credentials_questions)
        return credentials_ans["pwd"]

    credentials_questions = [
        inquirer.Text("id", message="Please Enter Your ID"),
        inquirer.Password("pwd", message="Please Enter Your SIS Password"),
        inquirer.List(
            "save",
            message="Save Your Credentials for Future Use?",
            choices=["Yes", "No"],
            default="Yes"
        ),
    ]
    credentials_ans = inquirer.prompt(credentials_questions)
    save_credentials = credentials_ans["save"] == "Yes"
    credentials_path = os.path.join(
        BASE_DIR,
        "saved",
        f"{credentials_ans['id']}-credentials.json"
    )

    if save_credentials and not os.path.exists(credentials_path):
        with open(credentials_path, "w") as f:
            json.dump(
                {"id": credentials_ans['id'], "pwd": credentials_ans['pwd']},
                f,
                indent=4
            )

    return {"id": credentials_ans['id'], "pwd": credentials_ans['pwd']}


def student() -> Union[SIS, None]:
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
        user_creds = get_credentials()
    else:
        with open(
            os.path.join(
                BASE_DIR, "saved", f"{id_choice}-credentials.json"
            ), "r"
        ) as f:
            user_creds = json.load(f)

        pwd_changed = [
            inquirer.List(
                "save",
                message="Did You Change Your Password?",
                choices=["No", "Yes"],
                default="No"
            ),
        ]
        changed = inquirer.prompt(pwd_changed)["save"] == "Yes"
        if changed:
            os.remove(
                os.path.join(
                    BASE_DIR, "saved", f"{id_choice}-credentials.json"
                )
            )
            user_creds["pwd"] = get_credentials(True)
            save_pwd = [
                inquirer.List(
                    "save",
                    message="Save Your New Credentials for Future Use?",
                    choices=["Yes", "No"],
                    default="Yes"
                ),
            ]
            save = inquirer.prompt(save_pwd)["save"] == "Yes"
            if save:
                with open(
                    os.path.join(
                        BASE_DIR, "saved", f"{id_choice}-credentials.json"
                    ), "w"
                ) as f:
                    json.dump(user_creds, f, indent=4)

    return SIS(user_creds["id"], user_creds["pwd"])


def main() -> None:
    welcome()

    if FIRST_USE:
        print("It seems like this is your first time using EJUSTIAN CLI or you don't have any saved credentials.")
        print("Please enter your SIS credentials to get started.")
        print("Note: Your credentials are stored locally and are only used to log you in to SIS.")
        print("They are never sent to any third party.")

        save_data = get_credentials()
        with Loader("\033[92m" + "Please wait while logging you in..." + "\033[0m", "Thanks for waiting!"):
            print("\033[0m")
            SIS(save_data["id"], save_data["pwd"]).info

        print("Thank You! You are now ready to use EJUSTIAN CLI.")
        print("Enjoy!\n")

    user_options = [
        inquirer.List(
            'opts',
            message="What Do You Want to Do?",
            choices=[
                "Show your SIS data (excluding your CGPA, GPA, Passed CH, and Remaining CH)",
                "Show your CGPA",
                "Show your credit hours (Passed CH, Remaining CH)",
                "Attendance tracker",
                "Task manager (kanban style)",
                "Connect to the nearest WiFi",
                "E-JUST map",
                "Exit",
            ],
        )
    ]

    while True:
        user_choice = inquirer.prompt(user_options)["opts"]

        if user_choice == "Exit":
            print("Thank you for using EJUSTIAN CLI!")
            print("Bye!\n")
            break

        if user_choice == "Show your SIS data (excluding your CGPA, GPA, Passed CH, and Remaining CH)":
            if not (user := student()):
                continue
            with Loader("\033[92m" + "Please wait while getting your data...", "Thanks for waiting!"):
                print("\n\n" + "\033[0m" + user.info + "\n")
        elif user_choice == "Show your CGPA":
            if not (user := student()):
                continue
            with Loader("\033[92m" + "Please wait while getting your data...", "Thanks for waiting!"):
                print("\n\n" + "\033[0m" + user.cgpa + "\n")
        elif user_choice == "Show your credit hours (Passed CH, Remaining CH)":
            if not (user := student()):
                continue
            with Loader("\033[92m" + "Please wait while getting your data...", "Thanks for waiting!"):
                print("\n\n" + "\033[0m" + user.credit_hours + "\n")
        elif user_choice == "Attendance tracker":
            if not (user := student()):
                continue
            with Loader("\033[92m" + "Please wait while getting your data...", "Thanks for waiting!"):
                print("\n\n" + "\033[0m" + user.attendance + "\n")
        elif user_choice == "Task manager (kanban style)":
            start_kanban()
        elif user_choice == "Connect to the nearest WiFi":
            continue
        elif user_choice == "E-JUST map":
            print(MAP)


if __name__ == "__main__":
    main()
