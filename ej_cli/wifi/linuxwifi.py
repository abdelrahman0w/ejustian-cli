import subprocess


class LinuxWiFi:
    def __init__(self) -> None:
        pass

    @property
    def is_active(self) -> bool:
        process = subprocess.run(
            ["nmcli", "-t", "-f", "ACTIVE,SSID", "dev", "wifi"],
            stdout=subprocess.PIPE
        )

        if process.returncode != 0:
            return False

        try:
            wifi_list = [
                wifi.split(":")
                for wifi in process.stdout.decode("utf-8").strip().split("\n")
            ]
            return any("yes" in wifi for wifi in wifi_list)
        except Exception:
            return False

    @property
    def scan(self) -> list:
        process = subprocess.run(
            ["nmcli", "-t", "-f", "SSID,SIGNAL", "dev", "wifi"],
            stdout=subprocess.PIPE
        )

        if process.returncode != 0:
            return []

        try:
            return [
                wifi.split(":") for wifi in process.stdout.decode("utf-8").strip().split("\n")
            ]
        except Exception:
            return []

    def is_connected_to(self, ssid: str) -> bool:
        process = subprocess.run(
            ["nmcli", "-t", "-f", "ACTIVE,SSID", "dev", "wifi"],
            stdout=subprocess.PIPE
        )

        if process.returncode != 0:
            return False

        try:
            wifi_list = [
                wifi.split(":")
                for wifi in process.stdout.decode("utf-8").strip().split("\n")
            ]
            return ["yes", ssid] in wifi_list
        except Exception:
            return False

    def connect_to(self, ssid: str, password: str):
        subprocess.call(
            [
                'nmcli', 'd', 'wifi',
                'connect', ssid,
                'password', password
            ]
        )

        return "CONNECTED SUCCESSFULLY!" if self.is_connected_to(ssid) else "AN ERROR OCCURED!"
