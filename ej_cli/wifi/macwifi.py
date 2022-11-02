import subprocess
from typing import Generator


class MacWiFi:
    def __init__(self) -> None:
        pass

    @property
    def is_active(self) -> bool:
        return False

    @property
    def scan(self) -> list:
        def extract_ssid_rssi(string) -> Generator:
            lines = string.splitlines()[1:]
            for line in lines:
                if line:
                    ssid, _, rssi, *_ = map(str.strip, line.rsplit(maxsplit=7))
                    rssi = rssi[1:]
                    yield ssid, rssi

        process = subprocess.run(
            [
                "/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport",
                "-s"
            ],
            stdout=subprocess.PIPE
        )

        if process.returncode != 0:
            return []

        try:
            return list(extract_ssid_rssi(process))
        except Exception:
            return []

    def is_connected_to(self, ssid: str) -> bool:
        return False

    def connect_to(self, ssid: str, password: str):
        subprocess.call(
            [
                "networksetup", "-setairportnetwork",
                "en0", ssid, password
            ]
        )
