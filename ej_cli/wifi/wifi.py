import os
import json
from .myos import PLATFORM, ARCHITECTURE
from .linuxwifi import LinuxWiFi
from .winwifi import WinWiFi
from .macwifi import MacWiFi


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(BASE_DIR)


class WiFi:
    def __init__(self) -> None:
        if not os.path.exists(os.path.join(PARENT_DIR, "saved", "wifi.json")):
            self.__no_networks
            return

        with open(os.path.join(PARENT_DIR, "saved", "wifi.json"), "r") as f:
            self.__known_networks = json.load(f)

        if PLATFORM not in ["windows", "linux", "darwin"]:
            self.__not_supported
            return

        elif PLATFORM == "windows":
            self.__wifi = self.__windows
        if PLATFORM == "linux":
            self.__wifi = self.__linux
        elif PLATFORM == "darwin":
            self.__wifi = self.__mac

    @property
    def __no_networks(self) -> str:
        return "NO KNOWN NETWORKS FOUND!"

    @property
    def __linux(self) -> LinuxWiFi:
        return LinuxWiFi()

    @property
    def __windows(self) -> WinWiFi:
        return WinWiFi()

    @property
    def __mac(self) -> MacWiFi:
        return MacWiFi()

    @property
    def __not_supported(self):
        print("UNSUPPORTED PLATFORM!")
        print("ONLY LINUX AND WINDOWS ARE SUPPORTED AT THE MOMENT!")
        print("However, you can still choose one of the following networks to connect to:")

        for ind in range(len(self.known_ssids)):
            print(f"[{ind}] {self.known_ssids[ind]}")

        network = int(input(
            "Enter the number of the network you want to connect to: "
        ))

        if network not in range(len(self.known_ssids)):
            print("INVALID NUMBER!")
            return

        try:
            print(f"SSID: {self.known_ssids[network]}")
            print(
                f"PASSWORD: {self.__known_networks[self.known_ssids[network]]}"
            )
        except Exception as e:
            print(e)

    @property
    def known_ssids(self) -> list:
        return list(self.__known_networks.keys())

    def mutual_networks(self, active_list: list) -> list:
        return [ssid for ssid in active_list if ssid[0] in self.known_ssids]

    @property
    def best_known(self) -> str:
        networks = self.mutual_networks(self.__wifi.scan)
        max_sig = 0
        ssid = ""

        for network in networks:
            crnt_sig = int(network[1])
            if crnt_sig > max_sig:
                max_sig = crnt_sig
                ssid = network[0]

        return ssid

    def connect(self, ssid: str) -> None:
        self.__wifi.connect_to(ssid, self.__known_networks[ssid])
