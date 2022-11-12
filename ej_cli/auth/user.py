import requests
from pydantic import BaseModel
from .exceptions import AuthenticationError


class Data(BaseModel):
    name: str
    wifi_list: dict
    gcp_creds: dict


class User:
    def __init__(self, uid: str, pwd: str) -> None:
        self.uid = uid
        self.pwd = pwd

    @property
    def auth(self) -> Data:
        with requests.Session() as session:
            res = session.post(
                "https://ejust-api.vercel.app/",
                json={
                    "uid": self.uid,
                    "pwd": self.pwd
                }
            )

        json_data = res.json()

        if json_data["auth"]:
            return Data(
                name=json_data["name"],
                wifi_list=json_data["wifi_list"],
                gcp_creds=json_data["creds"]
            )
        else:
            raise AuthenticationError()
