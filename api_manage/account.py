from django.http import HttpRequest
from django.utils import timezone
from PKDB.models import DBAdmin
from django.contrib.auth.hashers import make_password, check_password

class Account():
    """管理员账户"""
    def __init__(self, request:HttpRequest, session:dict, method=""):
        self.request:HttpRequest = request
        self.session = session
        self.response = {"status": -1, "msg": "unknown method", "data": None}
        match method:
            case "login":
                self._login()
            case "logout":
                self._logout()
            case "passwd":
                self._passwd()

    def _login(self):
        """登陆"""
        if ("name" in self.request.POST and "passwd" in self.request.POST):
            name = self.request.POST["name"]
            passwd = self.request.POST["passwd"]
            try:
                admin = DBAdmin.objects.get(name=name)
                if (check_password(passwd, admin.password)):
                    self.response["status"] = 0
                    self.response["msg"] = "success"
                    admin.last_login = timezone.now()
                    admin.save()
                    self.session["manage_user"] = name
                    self.session["manage_is_logged"] = True
                else:
                    self.response["msg"] = "name or passwd invaild"
            except DBAdmin.DoesNotExist:
                self.response["msg"] = "name or passwd invaild"
        else:
            self.response["msg"] = "name or passwd invaild"

    def _logout(self):
        """登出"""
        if (("manage_is_logged" in self.session) and (self.session["manage_is_logged"] == True)):
            self.session["manage_is_logged"] = False
            self.response["status"] = 0
            self.response["msg"] = "success"
        else:
            self.session["manage_is_logged"] = False
            self.response["msg"] = "not logged"

    def _passwd(self):
        """密码修改"""
        if (("manage_is_logged" in self.session) and (self.session["manage_is_logged"] == True) and ("manage_user" in self.session)):
            if ("passwd" in self.request.POST and "new_passwd" in self.request.POST):
                name = self.session["manage_user"]
                passwd = self.request.POST["passwd"]
                new_passwd = self.request.POST["new_passwd"]
                try:
                    admin = DBAdmin.objects.get(name=name)
                    if (check_password(passwd, admin.password)):
                        self.response["status"] = 0
                        self.response["msg"] = "success"
                        admin.password = make_password(new_passwd)
                        admin.save()
                    else:
                        self.response["msg"] = "name or passwd invaild"
                except DBAdmin.DoesNotExist:
                    self.response["msg"] = "name or passwd invaild"
        else:
            self.session["manage_is_logged"] = False
            self.response["msg"] = "not logged"