from django.http import HttpRequest
from PKDB.models import DBUser, DBPlateNumber
from django.contrib.auth.hashers import make_password, check_password
from django.utils import timezone

class User():
    """用户查询管理"""
    def __init__(self, request:HttpRequest, session:dict, method=""):
        self.request:HttpRequest = request
        self.session = session
        self.response = {"status": -1, "msg": "unknown method", "data": None}
        if (("is_logged" not in self.session) or (self.session["is_logged"] != True)):
            if (method != "register" and method != "login"):
                self.response["msg"] = "not logged"
                return
        match method:
            case "register":
                self._register()
            case "login":
                self._login()
            case "logout":
                self._logout()
            case "info":
                self._info()
            case "modify":
                self._modify()
            case "passwd":
                self._passwd()

    def _register(self):
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
                user.save()
                self.response["status"] = 0
                self.response["msg"] = "success"
                self.session["user"] = user.name
                self.session["is_logged"] = True
        else:
            self.response["msg"] = "name or passwd invaild"

    def _login(self):
        """登陆"""
        if ("name" in self.request.POST and "passwd" in self.request.POST):
            name = self.request.POST["name"]
            passwd = self.request.POST["passwd"]
            try:
                user = DBUser.objects.get(name=name)
                if (check_password(passwd, user.password)):
                    self.response["status"] = 0
                    self.response["msg"] = "success"
                    user.last_login = timezone.now()
                    user.save()
                    self.session["user"] = user.name
                    self.session["is_logged"] = True
                else:
                    self.response["msg"] = "name or passwd invaild"
            except DBUser.DoesNotExist:
                self.response["msg"] = "name or passwd invaild"
        else:
            self.response["msg"] = "name or passwd invaild"

    def _logout(self):
        """登出"""
        self.session["is_logged"] = False
        self.response["status"] = 0
        self.response["msg"] = "success"

    def _info(self):
        """用户详细信息"""
        user = DBUser.objects.get(name=self.session["user"])
        data = {"info":{}}
        data["info"]["name"] = user.name
        data["info"]["phone"] = user.phone
        data["info"]["email"] = user.email
        data["info"]["balance"] = float(user.balance)
        data["info"]["register_time"] = user.register_time.astimezone(timezone.get_current_timezone()).strftime("%Y-%m-%d %H:%M:%S")
        if (user.last_login != None):
            data["info"]["last_login"] = user.last_login.astimezone(timezone.get_current_timezone()).strftime("%Y-%m-%d %H:%M:%S")
        else:
            data["info"]["last_login"] = ""
        data["info"]["plates"] = []
        plates = DBPlateNumber.objects.filter(user=user)
        for plate in plates.values():
            data["info"]["plates"].append(plate["plate"])
        self.response["data"] = data
        self.response["status"] = 0
        self.response["msg"] = "success"

    def _modify(self):
        """修改用户信息"""
        user = DBUser.objects.get(name=self.session["user"])
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
        user.save()
        self.response["status"] = 0
        self.response["msg"] = "success"

    def _passwd(self):
        """密码修改"""
        if ("passwd" in self.request.POST and "new_passwd" in self.request.POST):
            passwd = self.request.POST["passwd"]
            new_passwd = self.request.POST["new_passwd"]
            user = DBUser.objects.get(name=self.session["user"])
            if (check_password(passwd, user.password)):
                self.response["status"] = 0
                self.response["msg"] = "success"
                user.password = make_password(new_passwd)
                user.save()
            else:
                self.response["msg"] = "name or passwd invaild"
