import subprocess
import re


class WinWiFi:
    def __init__(self) -> None:
        self.networks = {}

    def is_active(self) -> bool:
        """
        Check if the WiFi is active.
        """
        command = 'netsh wlan show interfaces | findstr "State"'
        result = subprocess.run(command, shell=True, capture_output=True)
        return 'connected' in result.stdout.decode().lower()

    @property
    def scan(self) -> dict:
        """
        Scan for WiFi networks and return the password of 
        the strongest network if it's locally known.
        """
        command = 'netsh wlan show networks mode=bssid | findstr "^SSID Signal"'
        result = subprocess.run(command, shell=True, capture_output=True)
        x = re.findall(r'B?SSID.*|Signal.*', result.stdout.decode())
        # print(x)
        i = 0
        while i < len(x):
            if x[i][:4] == 'SSID':
                # print(x[i])
                ssid = re.findall(r':.*', x[i])[0].strip(': ').rstrip()
                signals = []
                i += 1
                while i < len(x) and x[i][:6] == 'Signal':
                    signals.append(
                        int(re.findall(r':.*', x[i])[0].strip(': ').replace('%', '')))
                    i += 1
                self.networks[ssid] = max(signals)
        return self.networks
        # return max(self.networks, key=self.networks.get)

    def is_connected_to(self, ssid: str) -> bool:
        """
        Check if the WiFi is connected to a specific network.
        """
        if not self.is_active():
            return False
        command = 'netsh wlan show interfaces | findstr "SSID"'
        result = subprocess.run(command, shell=True, capture_output=True)
        return ssid in result.stdout.decode()

    def connect_to(self, ssid: str, pwd: str) -> None:
        """
        Connect to a WiFi network.
        """
        command = f'netsh wlan connect name="{ssid}" ssid="{ssid}" key="{pwd}"'
        subprocess.run(command, shell=True, capture_output=True)
