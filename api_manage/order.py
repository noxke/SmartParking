from django.http import HttpRequest
from PKDB.models import DBUser, DBPlateNumber, DBOrder
from datetime import datetime
from django.utils import timezone
from decimal import Decimal

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
        sort_column = "id"
        sort = "asc"
        offset = 0
        limit = 0
        no_data = False
        if ("sort_column" in self.request.GET):
            if (self.request.GET["sort_column"] in ("id", "user_name", "plate", "price", "amount", "duration", "begin_time", "end_time")):
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
        match sort_column:
            case "user_name":
                query_result = []
                for user in DBUser.objects.order_by("name"):
                    user_id = user.id
                    query_result.extend(list(DBOrder.objects.filter(user=user_id).values()))
            case "plate":
                query_result = []
                for plate in DBPlateNumber.objects.order_by("plate"):
                    plate_id = plate.id
                    query_result.extend(list(DBOrder.objects.filter(plate=plate_id).values()))
            case "end_time":
                query_result = list(DBOrder.objects.filter(end_time__isnull=False).order_by("end_time").values())
                query_result.extend(list(DBOrder.objects.filter(end_time__isnull=True).values()))
            case _:
                query_result = list(DBOrder.objects.order_by(sort_column).values())
        print(query_result)
        if (sort == "desc"):
            query_result = query_result[::-1]
        if (limit == 0):
            query_result = query_result[offset:]
        else:
            query_result = query_result[offset:offset+limit]
        data = {"count":len(query_result), "query":[]}
        if (no_data == False):
            for query in query_result:
                plate_id = query.pop("plate_id")
                query["plate"] = DBPlateNumber.objects.get(id=plate_id).plate
                user_id = query.pop("user_id")
                query["user"] = DBUser.objects.get(id=user_id).name
                query["price"] = float(query["price"])
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
                data["query"].append(query)
        self.response["data"] = data
        self.response["status"] = 0
        self.response["msg"] = "success"


    def _info(self):
        """订单详细信息"""
        query_column = "null"
        query_value = None
        for q in ("id", "user_name", "plate"):
            if (q in self.request.POST):
                query_column = q
                query_value = self.request.POST[q]
                break
        query_result = []
        match query_column:
            case "id":
                query_result = list(DBOrder.objects.filter(id=int(query_value)).values())
            case "user_name":
                try:
                    user_id = DBUser.objects.get(name=query_value).id
                    query_result = list(DBOrder.objects.filter(user=user_id).values())
                except DBUser.DoesNotExist:
                    pass
            case "plate":
                try:
                    plate_id = DBPlateNumber.objects.get(plate=query_value).id
                    query_result = list(DBOrder.objects.filter(plate=plate_id).values())
                except DBPlateNumber.DoesNotExist:
                    pass
            case _:
                if ("begin_time" in self.request.POST):
                    begin_time = datetime.strptime(self.request.POST["begin_time"], "%Y-%m-%d %H:%M:%S")
                    begin_time = timezone.make_aware(begin_time)
                    if ("end_time" in self.request.POST):
                        end_time = datetime.strptime(self.request.POST["end_time"], "%Y-%m-%d %H:%M:%S")
                        end_time = timezone.make_aware(end_time)
                        query_result = list(DBOrder.objects.filter(end_time__isnull=False).filter(begin_time__gte=begin_time).filter(end_time__lte=end_time).order_by("begin_time").values())
                    else:
                        print(begin_time)
                        query_result = list(DBOrder.objects.filter(begin_time__gte=begin_time).order_by("begin_time").values())
                elif ("end_time" in self.request.POST):
                    end_time = datetime.strptime(self.request.POST["end_time"], "%Y-%m-%d %H:%M:%S")
                    end_time = timezone.make_aware(end_time)
                    query_result = list(DBOrder.objects.filter(end_time__isnull=False).filter(end_time__lte=end_time).order_by("-end_time").values())
                else:
                    self.response["msg"] = "query invaild"
                    return
        data = {"count":len(query_result), "info":[]}
        for query in query_result:
            plate_id = query.pop("plate_id")
            query["plate"] = DBPlateNumber.objects.get(id=plate_id).plate
            user_id = query.pop("user_id")
            query["user"] = DBUser.objects.get(id=user_id).name
            query["price"] = float(query["price"])
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

    def _add(self):
        """订单新增"""
        if (("plate" in self.request.POST) and ("price" in self.request.POST)):
            price = Decimal(self.request.POST["price"])
            try:
                plate = DBPlateNumber.objects.get(plate=self.request.POST["plate"])
                user = plate.user
                order = DBOrder(plate=plate, user=user, price=price)
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
                    except DBUser.DoesNotExist:
                        self.response["msg"] = "plate not exists"
                        return
                if ("price" in self.request.POST):
                    order.price = Decimal(self.request.POST["price"])
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
