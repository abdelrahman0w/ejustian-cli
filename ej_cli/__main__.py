import os
import json
from bullet import Bullet, colors, Input, YesNo, Password
from .sis.sis import SIS
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


def main() -> None:
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
    print("The command line interface app that allows EJUST students to manage all their stuff.")

    if FIRST_USE:
        print("\nIt seems like this is your first time using EJUSTIAN CLI or you don't have any saved credentials.")
        print("Please enter your SIS credentials to get started.")
        print("Note: Your credentials are stored locally and are only used to log you in to SIS.")
        print("They are never sent to any third party.\n")

        user_id = Input(
            "Please Enter Your SIS ID: "
        ).launch()
        pwd = Password(
            "Please Enter Your SIS Password: "
        ).launch()

        if save_credentials := YesNo(
            "Do you want to save your credentials for future use?"
        ).launch():
            sis_account = SIS(id=user_id, pwd=pwd, save_credentials=True)
        else:
            sis_account = SIS(id=user_id, pwd=pwd, save_credentials=False)

        sis_account.info

        print("Thank You! You are now ready to use EJUSTIAN CLI.")
        print("Enjoy!")

    menu = Bullet(
        prompt="What do you want to do?",
        choices=[
            "Show your SIS data (excluding your CGPA, GPA, Passed CH, and Remaining CH)",
            "Show your CGPA",
            "Show your credit hours (Passed CH, Remaining CH)",
            "Attendance tracker",
            "Task manager (kanban style)",
            "Exit",
        ],
        indent=0,
        align=1,
        margin=1,
        shift=0,
        bullet=">",
        bullet_color=colors.foreground["green"],
        pad_right=1,
    )

    while True:
        choice = menu.launch()
        if choice == "Show your SIS data (excluding your CGPA, GPA, Passed CH, and Remaining CH)":
            id_list = [
                file.split("-")[0]
                for file in os.listdir(os.path.join(BASE_DIR, "saved"))
                if file.endswith("-credentials.json")
            ]
            id_list.extend(["Enter a new ID", "Back"])
            id_menu = Bullet(
                prompt="Which ID do you want to use?",
                choices=id_list,
                indent=0,
                align=1,
                margin=1,
                shift=0,
                bullet=">",
                bullet_color=colors.foreground["green"],
                pad_right=1,
            )
            id_choice = id_menu.launch()

            if id_choice == "Enter a new ID":
                user_id = Input(
                    "Please Enter Your SIS ID: "
                ).launch()
                pwd = Password(
                    "Please Enter Your SIS Password: "
                ).launch()

                if save_credentials := YesNo(
                    "Do you want to save your credentials for future use?"
                ).launch():
                    sis_account = SIS(id=user_id, pwd=pwd,
                                      save_credentials=True)
                else:
                    sis_account = SIS(id=user_id, pwd=pwd,
                                      save_credentials=False)

                sis_account.info

            elif id_choice == "Back":
                continue

            else:
                if YesNo(prompt="Did you change your password?", default="n").launch():
                    pwd = Password(
                        "Please Enter Your New SIS Password: "
                    ).launch()

                    if save_credentials := YesNo(
                        "Do you want to save your credentials for future use?"
                    ).launch():
                        sis_account = SIS(
                            id=id_choice, pwd=pwd,
                            save_credentials=True, new_pwd=True
                        )
                        print("Your password has been updated successfully.")
                    else:
                        sis_account = SIS(
                            id=id_choice, pwd=pwd,
                            save_credentials=False, new_pwd=True
                        )

                else:
                    with open(os.path.join(BASE_DIR, "saved", f"{id_choice}-credentials.json"), "r") as f:
                        pwd = json.load(f)["pwd"]

                    sis_account = SIS(id=id_choice, pwd=pwd)

            print("\nThis is your requested info:")
            print(sis_account.info)

            another_action = YesNo(
                prompt="Do you want to do any other action?",
            ).launch()

            if another_action:
                continue
            print("Thank you for using EJUSTIAN CLI!\nBye!")
            break

        elif choice == "Show your CGPA":
            id_list = [
                file.split("-")[0]
                for file in os.listdir(os.path.join(BASE_DIR, "saved"))
                if file.endswith("-credentials.json")
            ]
            id_list.extend(["Enter a new ID", "Back"])
            id_menu = Bullet(
                prompt="Which ID do you want to use?",
                choices=id_list,
                indent=0,
                align=1,
                margin=1,
                shift=0,
                bullet=">",
                bullet_color=colors.foreground["green"],
                pad_right=1,
            )
            id_choice = id_menu.launch()

            if id_choice == "Enter a new ID":
                user_id = Input(
                    "Please Enter Your SIS ID: "
                ).launch()
                pwd = Password(
                    "Please Enter Your SIS Password: "
                ).launch()

                if save_credentials := YesNo(
                    "Do you want to save your credentials for future use?"
                ).launch():
                    sis_account = SIS(id=user_id, pwd=pwd,
                                      save_credentials=True)
                else:
                    sis_account = SIS(id=user_id, pwd=pwd,
                                      save_credentials=False)

                sis_account.info

            elif id_choice == "Back":
                continue

            else:
                if YesNo(prompt="Did you change your password?", default="n").launch():
                    pwd = Password(
                        "Please Enter Your New SIS Password: "
                    ).launch()

                    if save_credentials := YesNo(
                        "Do you want to save your credentials for future use?"
                    ).launch():
                        sis_account = SIS(
                            id=id_choice, pwd=pwd,
                            save_credentials=True, new_pwd=True
                        )
                        print("Your password has been updated successfully.")
                    else:
                        sis_account = SIS(
                            id=id_choice, pwd=pwd,
                            save_credentials=False, new_pwd=True
                        )

                else:
                    with open(os.path.join(BASE_DIR, "saved", f"{id_choice}-credentials.json"), "r") as f:
                        pwd = json.load(f)["pwd"]

                    sis_account = SIS(id=id_choice, pwd=pwd)

            print("\nThis is your requested info:")
            print(sis_account.cgpa)

            another_action = YesNo(
                prompt="Do you want to do any other action?",
            ).launch()

            if another_action:
                continue
            print("Thank you for using EJUSTIAN CLI!\nBye!")
            break

        elif choice == "Show your credit hours (Passed CH, Remaining CH)":
            id_list = [
                file.split("-")[0]
                for file in os.listdir(os.path.join(BASE_DIR, "saved"))
                if file.endswith("-credentials.json")
            ]
            id_list.extend(["Enter a new ID", "Back"])
            id_menu = Bullet(
                prompt="Which ID do you want to use?",
                choices=id_list,
                indent=0,
                align=1,
                margin=1,
                shift=0,
                bullet=">",
                bullet_color=colors.foreground["green"],
                pad_right=1,
            )
            id_choice = id_menu.launch()

            if id_choice == "Enter a new ID":
                user_id = Input(
                    "Please Enter Your SIS ID: "
                ).launch()
                pwd = Password(
                    "Please Enter Your SIS Password: "
                ).launch()

                if save_credentials := YesNo(
                    "Do you want to save your credentials for future use?"
                ).launch():
                    sis_account = SIS(id=user_id, pwd=pwd,
                                      save_credentials=True)
                else:
                    sis_account = SIS(id=user_id, pwd=pwd,
                                      save_credentials=False)

                sis_account.info

            elif id_choice == "Back":
                continue

            else:
                if YesNo(prompt="Did you change your password?", default="n").launch():
                    pwd = Password(
                        "Please Enter Your New SIS Password: "
                    ).launch()

                    if save_credentials := YesNo(
                        "Do you want to save your credentials for future use?"
                    ).launch():
                        sis_account = SIS(
                            id=id_choice, pwd=pwd,
                            save_credentials=True, new_pwd=True
                        )
                        print("Your password has been updated successfully.")
                    else:
                        sis_account = SIS(
                            id=id_choice, pwd=pwd,
                            save_credentials=False, new_pwd=True
                        )
                else:
                    with open(os.path.join(BASE_DIR, "saved", f"{id_choice}-credentials.json"), "r") as f:
                        pwd = json.load(f)["pwd"]

                    sis_account = SIS(id=id_choice, pwd=pwd)

            print("\nThis is your requested info:")
            print(sis_account.credit_hours)

            another_action = YesNo(
                prompt="Do you want to do any other action?",
            ).launch()

            if another_action:
                continue
            print("Thank you for using EJUSTIAN CLI!\nBye!")
            break

        elif choice == "Attendance tracker":
            id_list = [
                file.split("-")[0]
                for file in os.listdir(os.path.join(BASE_DIR, "saved"))
                if file.endswith("-credentials.json")
            ]
            id_list.extend(["Enter a new ID", "Back"])
            id_menu = Bullet(
                prompt="Which ID do you want to use?",
                choices=id_list,
                indent=0,
                align=1,
                margin=1,
                shift=0,
                bullet=">",
                bullet_color=colors.foreground["green"],
                pad_right=1,
            )
            id_choice = id_menu.launch()

            if id_choice == "Enter a new ID":
                user_id = Input(
                    "Please Enter Your SIS ID: "
                ).launch()
                pwd = Password(
                    "Please Enter Your SIS Password: "
                ).launch()

                if save_credentials := YesNo(
                    "Do you want to save your credentials for future use?"
                ).launch():
                    sis_account = SIS(id=user_id, pwd=pwd,
                                      save_credentials=True)
                else:
                    sis_account = SIS(id=user_id, pwd=pwd,
                                      save_credentials=False)

            elif id_choice == "Back":
                continue

            else:
                if YesNo(prompt="Did you change your password?", default="n").launch():
                    pwd = Password(
                        "Please Enter Your New SIS Password: "
                    ).launch()

                    if save_credentials := YesNo(
                        "Do you want to save your credentials for future use?"
                    ).launch():
                        sis_account = SIS(
                            id=id_choice, pwd=pwd,
                            save_credentials=True, new_pwd=True
                        )
                        print("Your password has been updated successfully.")
                    else:
                        sis_account = SIS(
                            id=id_choice, pwd=pwd,
                            save_credentials=False, new_pwd=True
                        )
                else:
                    with open(os.path.join(BASE_DIR, "saved", f"{id_choice}-credentials.json"), "r") as f:
                        pwd = json.load(f)["pwd"]

                    sis_account = SIS(id=id_choice, pwd=pwd)

            print("\nThis is your requested info:")
            print(sis_account.attendance)

            another_action = YesNo(
                prompt="Do you want to do any other action?",
            ).launch()

            if another_action:
                continue
            print("Thank you for using EJUSTIAN CLI!\nBye!")
            break

        elif choice == "Task manager (kanban style)":
            start_kanban()

        elif choice == "Exit":
            print("Thank you for using EJUSTIAN CLI!\nBye!")
            break


if __name__ == "__main__":
    main()
