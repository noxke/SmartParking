from django.http import HttpRequest
from PKDB.models import DBUser, DBPlateNumber

class Plate():
    """车牌查询管理"""
    def __init__(self, request:HttpRequest, session:dict, method=""):
        self.request:HttpRequest = request
        self.session = session
        self.response = {"status": -1, "msg": "unknown method", "data": None}
        if (("is_logged" not in self.session) or (self.session["is_logged"] != True)):
            self.response["msg"] = "not logged"
            return
        match method:
            case "add":
                self._add()
            case "del":
                self._del()

    def _add(self):
        """车牌新增"""
        if ("plate" in self.request.POST):
            plate_num = self.request.POST["plate"]
            try:
                plate = DBPlateNumber.objects.get(plate=plate_num)
                self.response["msg"] = "plate already exists"
            except DBPlateNumber.DoesNotExist:
                user = DBUser.objects.get(name=self.session["user"])
                plate = DBPlateNumber(plate=plate_num, user=user)
                plate.save()
                self.response["status"] = 0
                self.response["msg"] = "success"
        else:
            self.response["msg"] = "plate invaild"

    def _del(self):
        """车牌删除"""
        if ("plate" in self.request.POST):
            plate_num = self.request.POST["plate"]
            user = DBUser.objects.get(name=self.session["user"])
            try:
                plate = DBPlateNumber.objects.filter(user=user).get(plate=plate_num)
                plate.delete()
                self.response["status"] = 0
                self.response["msg"] = "success"
            except DBPlateNumber.DoesNotExist:
                self.response["msg"] = "plate not exists"
        else:
            self.response["msg"] = "plate invaild"

