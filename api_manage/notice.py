from django.http import HttpRequest
from PKDB.models import DBNotice
from django.utils import timezone
from datetime import datetime

class Notice():
    """通知查询管理"""
    def __init__(self, request:HttpRequest, session:dict, method=""):
        self.request:HttpRequest = request
        self.session = session
        self.response = {"status": -1, "msg": "unknown method", "data": None}
        if (("manage_is_logged" not in self.session) or (self.session["manage_is_logged"] != True)):
            self.response["msg"] = "not logged"
            return
        match method:
            case "query":
                self._query()
            case "add":
                self._add()
            case "modify":
                self._modify()
            case "del":
                self._del()

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

    def _add(self):
        """通知新增"""
        if ("title" in self.request.POST and "content" in self.request.POST):
            title = self.request.POST["title"]
            content = self.request.POST["content"]
            notice = DBNotice(title=title, content=content)
            notice.save()
            if ("create_time" in self.request.POST):
                create_time = datetime.strptime(self.request.POST["create_time"], "%Y-%m-%d %H:%M:%S")
                notice.begin_time = timezone.make_aware(create_time)
            self.response["status"] = 0
            self.response["msg"] = "success"
        else:
            self.response["msg"] = "params invaild"

    def _modify(self):
        """通知编辑"""
        if ("id" in self.request.POST):
            try:
                notice = DBNotice.objects.get(id=int(self.request.POST["id"]))
                if ("title" in self.request.POST):
                    notice.title = self.request.POST["title"]
                if ("content" in self.request.POST):
                    notice.content = self.request.POST["content"]
                if ("create_time" in self.request.POST):
                    create_time = datetime.strptime(self.request.POST["create_time"], "%Y-%m-%d %H:%M:%S")
                    notice.begin_time = timezone.make_aware(create_time)
                notice.save()
                self.response["status"] = 0
                self.response["msg"] = "success"
            except DBNotice.DoesNotExist:
                self.response["msg"] = "params invaild"
        else:
            self.response["msg"] = "query invaild"


    def _del(self):
        """通知删除"""
        if ("id" in self.request.POST):
            notice_id = self.request.POST["id"]
            try:
                notice = DBNotice.objects.get(id=notice_id)
                notice.delete()
                self.response["status"] = 0
                self.response["msg"] = "success"
            except DBNotice.DoesNotExist:
                self.response["msg"] = "params invaild"
        else:
            self.response["msg"] = "query invaild"
