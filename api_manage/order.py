from django.http import HttpRequest
from PKDB.models import DBUser, DBPlateNumber, DBOrder, DBSpot
from datetime import datetime
from django.utils import timezone


class Order():
    """订单查询管理"""
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
        """订单查询"""
        query_result = None
        if ("user_name" in self.request.GET):
            try:
                user = DBUser.objects.get(name=self.request.GET["user_name"])
                if (query_result == None):
                    query_result = DBOrder.objects.filter(user=user)
                else:
                    query_result = query_result.filter(user=user)
            except DBUser.DoesNotExist:
                pass
        if ("plate" in self.request.GET):
            try:
                plate = DBPlateNumber.objects.get(plate=self.request.GET["plate"])
                if (query_result == None):
                    query_result = DBOrder.objects.filter(plate=plate)
                else:
                    query_result = query_result.filter(plate=plate)
            except DBPlateNumber.DoesNotExist:
                pass
        if ("spot" in self.request.GET):
            try:
                spot = DBSpot.objects.get(spot=self.request.GET["spot"])
                if (query_result == None):
                    query_result = DBOrder.objects.filter(spot=spot)
                else:
                    query_result = query_result.filter(spot=spot)
            except DBSpot.DoesNotExist:
                pass
        if ("status" in self.request.GET):
            if (query_result == None):
                query_result = DBOrder.objects.filter(status=int(self.request.GET["status"]))
            else:
                query_result = query_result.filter(status=int(self.request.GET["status"]))
        if ("begin_time" in self.request.POST):
            begin_time = datetime.strptime(self.request.POST["begin_time"], "%Y-%m-%d %H:%M:%S")
            begin_time = timezone.make_aware(begin_time)
            if ("end_time" in self.request.POST):
                end_time = datetime.strptime(self.request.POST["end_time"], "%Y-%m-%d %H:%M:%S")
                end_time = timezone.make_aware(end_time)
                if (query_result == None):
                    query_result = DBOrder.objects.filter(end_time__isnull=False).filter(begin_time__gte=begin_time).filter(end_time__lte=end_time).order_by("begin_time")
                else:
                    query_result = query_result.filter(end_time__isnull=False).filter(begin_time__gte=begin_time).filter(end_time__lte=end_time).order_by("begin_time")
            else:
                if (query_result == None):
                    query_result = DBOrder.objects.filter(begin_time__gte=begin_time).order_by("begin_time")
                else:
                    query_result = query_result.filter(begin_time__gte=begin_time).order_by("begin_time")
        elif ("end_time" in self.request.POST):
            end_time = datetime.strptime(self.request.POST["end_time"], "%Y-%m-%d %H:%M:%S")
            end_time = timezone.make_aware(end_time)
            if (query_result == None):
                query_result = DBOrder.objects.filter(end_time__isnull=False).filter(end_time__lte=end_time).order_by("-end_time")
            else:
                query_result = query_result.filter(end_time__isnull=False).filter(end_time__lte=end_time).order_by("-end_time")
        if (query_result == None):
            query_result = DBOrder.objects

        sort_column = "id"
        sort = "asc"
        offset = 0
        limit = 0
        no_data = False
        if ("sort_column" in self.request.GET):
            if (self.request.GET["sort_column"] in ("id", "user_name", "plate", "spot", "amount", "duration", "begin_time", "end_time")):
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
        query_result_ls = []
        match sort_column:
            case "user_name":
                for user in DBUser.objects.order_by("name"):
                    user = user.id
                    query_result_ls.extend(list(query_result.filter(user=user).values()))
            case "plate":
                for plate in DBPlateNumber.objects.order_by("plate"):
                    plate = plate.id
                    query_result_ls.extend(list(query_result.filter(plate=plate).values()))
            case "spot":
                for spot in DBSpot.objects.order_by("spot"):
                    spot = spot.id
                    query_result_ls.extend(list(query_result.filter(spot=spot).values()))
            case "end_time":
                query_result_ls = list(query_result.filter(end_time__isnull=False).order_by("end_time").values())
                query_result_ls.extend(list(query_result.filter(end_time__isnull=True).values()))
            case _:
                query_result_ls = list(query_result.values())
        if (sort == "desc"):
            query_result_ls = query_result_ls[::-1]
        if (limit == 0):
            query_result_ls = query_result_ls[offset:]
        else:
            query_result_ls = query_result_ls[offset:offset+limit]
        data = {"count":len(query_result_ls), "info":[]}
        if (no_data == False):
            for query in query_result_ls:
                plate = query.pop("plate_id")
                query["plate"] = DBPlateNumber.objects.get(id=plate).plate
                user = query.pop("user_id")
                query["user_name"] = DBUser.objects.get(id=user).name
                spot = query.pop("spot_id")
                query["spot"] = DBSpot.objects.get(id=spot).spot
                query["amount"] = float(query["amount"])
                query["begin_time"] = query["begin_time"].astimezone(timezone.get_current_timezone()).strftime("%Y-%m-%d %H:%M:%S")
                if (query["end_time"] != None):
                    query["end_time"] = query["end_time"].astimezone(timezone.get_current_timezone()).strftime("%Y-%m-%d %H:%M:%S")
                else:
                    query["end_time"] = ""
                total_seconds = int(query["duration"].total_seconds())
                hours = total_seconds // 3600
                minutes = (total_seconds % 3600) // 60
                seconds = total_seconds % 60
                query["duration"] = "{}:{:02d}:{:02d}".format(hours, minutes, seconds)
                data["info"].append(query)
        self.response["data"] = data
        self.response["status"] = 0
        self.response["msg"] = "success"

    def _info(self):
        """订单详细信息"""
        if ("id" in self.request.GET):
            querys = DBOrder.objects.filter(id=int(self.request.GET["id"])).values()
            if (len(querys) != 1):
                self.response["msg"] = "order not exists"
                return
            query = querys[0]
            plate_id = query.pop("plate_id")
            query["plate"] = DBPlateNumber.objects.get(id=plate_id).plate
            user_id = query.pop("user_id")
            query["user_name"] = DBUser.objects.get(id=user_id).name
            spot_id = query.pop("spot_id")
            query["spot"] = DBSpot.objects.get(id=spot_id).spot
            query["amount"] = float(query["amount"])
            query["begin_time"] = query["begin_time"].astimezone(timezone.get_current_timezone()).strftime("%Y-%m-%d %H:%M:%S")
            if (query["end_time"] != None):
                query["end_time"] = query["end_time"].astimezone(timezone.get_current_timezone()).strftime("%Y-%m-%d %H:%M:%S")
            else:
                query["end_time"] = ""
            total_seconds = int(query["duration"].total_seconds())
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            seconds = total_seconds % 60
            query["duration"] = "{}:{:02d}:{:02d}".format(hours, minutes, seconds)
            self.response["data"] = query
            self.response["status"] = 0
            self.response["msg"] = "success"
        else:
            self.response["msg"] = "query invaild"

    def _add(self):
        """订单新增"""
        if (("plate" in self.request.POST) and ("spot" in self.request.POST)):
            try:
                plate = DBPlateNumber.objects.get(plate=self.request.POST["plate"])
                spot = DBSpot.objects.get(spot=self.request.POST["spot"])
                user = plate.user
                if ("status" in self.request.POST):
                    status = int(self.request.POST["status"])
                    if (status < 0 or status > 3):
                        self.response["msg"] = "params invaild"
                        return
                    order = DBOrder(plate=plate, user=user, status=status)
                else:
                    order = DBOrder(plate=plate, user=user)
                order.save()
                if ("begin_time" in self.request.POST):
                    begin_time = datetime.strptime(self.request.POST["begin_time"], "%Y-%m-%d %H:%M:%S")
                    order.begin_time = timezone.make_aware(begin_time)
                if ("end_time" in self.request.POST):
                    end_time = datetime.strptime(self.request.POST["end_time"], "%Y-%m-%d %H:%M:%S")
                    order.end_time = timezone.make_aware(end_time)
                order.save()
                self.response["status"] = 0
                self.response["msg"] = "success"
            except DBPlateNumber.DoesNotExist:
                self.response["msg"] = "plate not exists"
            except DBSpot.DoesNotExist:
                self.response["msg"] = "spot not exists"
        else:
            self.response["msg"] = "query invaild"

    def _del(self):
        """订单删除"""
        if ("id" in self.request.POST):
            order_id = int(self.request.POST["id"])
            try:
                order = DBOrder.objects.get(id=order_id)
                order.delete()
                self.response["status"] = 0
                self.response["msg"] = "success"
            except DBOrder.DoesNotExist:
                self.response["msg"] = "order not exists"
        else:
            self.response["msg"] = "query invaild"

    def _modify(self):
        """修改订单信息"""
        if ("id" in self.request.POST):
            order_id = int(self.request.POST["id"])
            try:
                order = DBOrder.objects.get(id=order_id)
                if ("plate" in self.request.POST):
                    try:
                        order.plate = DBPlateNumber.objects.get(plate=self.request.POST["plate"])
                        order.user = order.plate.user
                    except DBPlateNumber.DoesNotExist:
                        self.response["msg"] = "plate not exists"
                        return
                if ("spot" in self.request.POST):
                    try:
                        order.spot = DBSpot.objects.get(spot=self.request.POST["spot"])
                    except DBSpot.DoesNotExist:
                        self.response["msg"] = "spot not exists"
                        return
                if ("status" in self.request.POST):
                    status = int(self.request.POST["status"])
                    if (status < 0 or status > 3):
                        self.response["msg"] = "params invaild"
                        return
                    order.status = status
                if ("begin_time" in self.request.POST):
                    begin_time = datetime.strptime(self.request.POST["begin_time"], "%Y-%m-%d %H:%M:%S")
                    order.begin_time = timezone.make_aware(begin_time)
                if ("end_time" in self.request.POST):
                    end_time = datetime.strptime(self.request.POST["end_time"], "%Y-%m-%d %H:%M:%S")
                    order.end_time = timezone.make_aware(end_time)
                order.save()
                self.response["status"] = 0
                self.response["msg"] = "success"
            except DBUser.DoesNotExist:
                self.response["msg"] = "order not exists"
        else:
            self.response["msg"] = "query invaild"
