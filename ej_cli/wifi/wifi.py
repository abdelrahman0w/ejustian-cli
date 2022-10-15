import subprocess
from .myos import PLATFORM, ARCHITECTURE
from .user import User
from .linuxwifi import LinuxWiFi
from .winwifi import WinWiFi


class WiFi:
    def __init__(self, uid: str, pwd: str) -> None:
        self.user = User(uid, pwd).auth_ejustian
        if self.user["auth"]:
            self.user_name = self.user["name"]
            self.known_list = self.user["wifi_list"]
            self.ssid_list = list(self.known_list.keys())
        else:
            self.user_name = self.known_list = self.ssid_list = None
