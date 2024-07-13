from django.http import HttpRequest
from PKDB.models import DBPrice

class Price():
    """定价策略管理"""
    def __init__(self, request:HttpRequest, session:dict, method=""):
        self.request:HttpRequest = request
        self.session = session
        self.response = {"status": -1, "msg": "unknown method", "data": None}
        if (("manage_is_logged" not in self.session) or (self.session["manage_is_logged"] != True)):
            self.response["msg"] = "not logged"
            return
        match method:
            case "info":
                self._info()
            case "modify":
                self._modify()

    def _info(self):
        """定价策略查询"""
        query_ls = DBPrice.objects.get().query()
        self.response["status"] = 0
        self.response["msg"] = "success"
        self.response["data"] = {}
        self.response["data"]["count"] = len(query_ls)
        self.response["data"]["info"] = query_ls

    def _modify(self):
        """定价策略修改"""
        if ("price" in self.request.POST):
            if (DBPrice.objects.get().edit(self.request.POST["price"]) == True):
                self.response["status"] = 0
                self.response["msg"] = "success"
            else:
                self.response["msg"] = "params invaild"
        else:
            self.response["msg"] = "query invaild"

