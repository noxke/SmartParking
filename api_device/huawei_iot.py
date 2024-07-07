from django.http import HttpRequest
from PKDB.models import DBUser, DBPlateNumber, DBOrder

class HuaweiIOT():
    """华为云物联网平台交互"""
    def __init__(self, request:HttpRequest, method=""):
        self.request:HttpRequest = request
        self.response = {"status": -1, "msg": "unknown method", "data": None}
        match method:
            case "plate1":
                self._gate1()
            case "del":
                self._gate2()

    def _gate1(self):
        """入口"""
        self.response["status"] = 0
        self.response["msg"] = "success"

    def _gate2(self):
        """出口"""
        self.response["status"] = 0
        self.response["msg"] = "success"

