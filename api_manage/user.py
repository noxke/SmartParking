from django.http import HttpRequest
from PKDB.models import DBUser, DBPlateNumber
from django.contrib.auth.hashers import make_password
from django.utils import timezone

class User():
    """用户查询管理"""
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
            case "info":
                self._info()
            case "add":
                self._add()
            case "del":
                self._del()
            case "modify":
                self._modify()

    def _query(self):
        """用户查询"""
        sort_column = "id"
        sort = "asc"
        offset = 0
        limit = 0
        no_data = False
        if ("sort_column" in self.request.GET):
            if (self.request.GET["sort_column"] in ("id", "name", "balance", "phone", "email", "register_time", "last_login")):
                sort_column = self.request.GET["sort_column"]
        if ("sort" in self.request.GET):
            if (self.request.GET["sort"] == "desc"):
                sort = "desc"
        if ("off" in self.request.GET):
            offset = int(self.request.GET["off"])
        if ("limit" in self.request.GET):
            limit = int(self.request.GET["limit"])
        if ("no_data" in self.request.GET):
            if (self.request.GET["no_data"] != "0"):
                no_data = True
        if (sort == "desc"):
            query_result = list(DBUser.objects.order_by("-"+sort_column).values())
        else:
            query_result = list(DBUser.objects.order_by(sort_column).values())
        if (limit == 0):
            query_result = query_result[offset:]
        else:
            query_result = query_result[offset:offset+limit]
        data = {"count":len(query_result), "query":[]}
        if (no_data == False):
            for query in query_result:
                query.pop("password")
                query["balance"] = float(query["balance"])
                query["register_time"] = query["register_time"].astimezone(timezone.get_current_timezone()).strftime("%Y-%m-%d %H:%M:%S")
                if (query["last_login"] != None):
                    query["last_login"] = query["last_login"].astimezone(timezone.get_current_timezone()).strftime("%Y-%m-%d %H:%M:%S")
                else:
                    query["last_login"] = ""
                data["query"].append(query)
        self.response["data"] = data
        self.response["status"] = 0
        self.response["msg"] = "success"


    def _info(self):
        """用户详细信息"""
        query_column = "null"
        query_value = None
        for q in ("id", "name", "phone", "email", "plate"):
            if (q in self.request.POST):
                query_column = q
                query_value = self.request.POST[q]
                break
        users = None
        match query_column:
            case "id":
                users = DBUser.objects.filter(id=int(query_value))
            case "name":
                users = DBUser.objects.filter(name=query_value)
            case "phone":
                users = DBUser.objects.filter(phone=query_value)
            case "email":
                users = DBUser.objects.filter(email=query_value)
            case "plate":
                try:
                    user = DBPlateNumber.objects.get(plate=query_value).user
                    users= DBUser.objects.filter(id=user.id)
                except DBUser.DoesNotExist:
                    users = DBUser.objects.filter(id=-1)
            case _:
                self.response["msg"] = "query invaild"
                return
        data = {"count":users.count(), "info":[]}
        for query in users.values():
            query.pop("password")
            query["balance"] = float(query["balance"])
            query["register_time"] = query["register_time"].astimezone(timezone.get_current_timezone()).strftime("%Y-%m-%d %H:%M:%S")
            if (query["last_login"] != None):
                query["last_login"] = query["last_login"].astimezone(timezone.get_current_timezone()).strftime("%Y-%m-%d %H:%M:%S")
            else:
                query["last_login"] = ""
            query["plates"] = []
            plates = DBPlateNumber.objects.filter(user=int(query["id"]))
            for plate in plates.values():
                query["plates"].append(plate["plate"])
            data["info"].append(query)
        self.response["data"] = data
        self.response["status"] = 0
        self.response["msg"] = "success"

    def _add(self):
        """用户新增"""
        if ("name" in self.request.POST and "passwd" in self.request.POST):
            name = self.request.POST["name"]
            passwd = self.request.POST["passwd"]
            try:
                user = DBUser.objects.get(name=name)
                self.response["msg"] = "user already exists"
            except DBUser.DoesNotExist:
                user = DBUser(name=name, password=make_password(passwd))
                if ("phone" in self.request.POST):
                    user.phone = self.request.POST["phone"]
                if ("email" in self.request.POST):
                    user.email = self.request.POST["email"]
                if ("balance" in self.request.POST):
                    user.balance = int(self.request.POST["balance"])
                user.save()
                self.response["status"] = 0
                self.response["msg"] = "success"
        else:
            self.response["msg"] = "name or passwd invaild"

    def _del(self):
        """用户删除"""
        if ("name" in self.request.POST):
            name = self.request.POST["name"]
            try:
                user = DBUser.objects.get(name=name)
                user.delete()
                self.response["status"] = 0
                self.response["msg"] = "success"
            except DBUser.DoesNotExist:
                self.response["msg"] = "user not exists"
        else:
            self.response["msg"] = "name invaild"

    def _modify(self):
        """修改用户信息"""
        if ("name" in self.request.POST):
            name = self.request.POST["name"]
            try:
                user = DBUser.objects.get(name=name)
                if ("new_name" in self.request.POST):
                    try:
                        new_user = DBUser.objects.get(name=self.request.POST["new_name"])
                        self.response["msg"] = "user already exists"
                        return
                    except DBUser.DoesNotExist:
                        user.name = self.request.POST["new_name"]
                if ("phone" in self.request.POST):
                    user.phone = self.request.POST["phone"]
                if ("email" in self.request.POST):
                    user.email = self.request.POST["email"]
                if ("balance" in self.request.POST):
                    user.balance = int(self.request.POST["balance"])
                if ("passwd" in self.request.POST):
                    user.password = make_password(self.request.POST["passwd"])
                user.save()
                self.response["status"] = 0
                self.response["msg"] = "success"
            except DBUser.DoesNotExist:
                self.response["msg"] = "user not exists"
        else:
            self.response["msg"] = "name invaild"
