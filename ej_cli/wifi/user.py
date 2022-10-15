import requests


class User:
    def __init__(self, uid: str, pwd: str) -> None:
        self.uid = uid
        self.pwd = pwd

    @property
    def auth_ejustian(self) -> dict:
        with requests.Session() as session:
            res = session.post(
                "https://ejust-api.vercel.app/",
                json={
                    "uid": self.uid,
                    "pwd": self.pwd
                }
            )

        return res.json()
