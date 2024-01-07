import jsonpickle
from pydantic import BaseModel
from jsonpickle import encode,decode


class Response:
    success: bool
    data: dict
    message: str

    def __init__(self, success: bool, data: dict, message: str = ""):
        self.success=success
        self.data=data
        self.message = message

    @classmethod
    def ok(cls, data: dict = {}, message: str = ""):
        return decode(encode(cls(success=True, data=data, message=message)))

    @classmethod
    def fail(cls, data: dict = {}, message: str = ""):
        return decode(encode(cls(success=False, data=data, message=message)))
