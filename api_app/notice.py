from django.http import HttpRequest
from PKDB.models import DBNotice
from django.utils import timezone

class Notice():
    """通知查询"""
    def __init__(self, request:HttpRequest, session:dict, method=""):
        self.request:HttpRequest = request
        self.session = session
        self.response = {"status": -1, "msg": "unknown method", "data": None}
        if (("is_logged" not in self.session) or (self.session["is_logged"] != True)):
            self.response["msg"] = "not logged"
            return
        match method:
            case "query":
                self._query()

    def _query(self):
        """通知查询"""
        if ("id" in self.request.GET):
            query_result = DBNotice.objects.filter(id=int(self.request.GET["id"]))
        else:
            query_result = DBNotice.objects
        self.response["status"] = 0
        self.response["msg"] = "success"
        self.response["data"] = []
        for query in query_result.values():
            query["create_time"] = query["create_time"].astimezone(timezone.get_current_timezone()).strftime("%Y-%m-%d %H:%M:%S")
            self.response["data"].append(query)
