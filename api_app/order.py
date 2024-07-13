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
        if (("is_logged" not in self.session) or (self.session["is_logged"] != True)):
            self.response["msg"] = "not logged"
            return
        match method:
            case "query":
                self._query()
            case "info":
                self._info()

    def _query(self):
        """订单查询"""
        user = DBUser.objects.get(name=self.session["user"])
        query_result = DBOrder.objects.filter(user=user)
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
            if (self.request.GET["sort_column"] in ("id", "plate", "spot", "amount", "duration", "begin_time", "end_time")):
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
                user_id = query.pop("user_id")
                query["user_name"] = DBUser.objects.get(id=user_id).name
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
        user = DBUser.objects.get(name=self.session["user"])
        if ("id" in self.request.GET):
            querys = DBOrder.objects.filter(user=user).filter(id=int(self.request.GET["id"])).values()
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
