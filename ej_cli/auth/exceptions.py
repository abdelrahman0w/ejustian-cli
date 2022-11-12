class AuthenticationError(Exception):
    __module__ = Exception.__module__

    def __init__(self, message: str = "Wrong Credentials") -> None:
        self.message = message

    def __str__(self) -> str:
        return self.message
