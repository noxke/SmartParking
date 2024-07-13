from django.db import models
from datetime import timedelta
from decimal import Decimal
import json

class DBAdmin(models.Model):
    """管理员信息"""
    name = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=128)
    register_time = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(null=True)


class DBUser(models.Model):
    """用户信息"""
    name = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=128)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    phone = models.CharField(max_length=128, null=True)
    email = models.EmailField(max_length=128, null=True)
    register_time = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(null=True)


class DBPlateNumber(models.Model):
    """车牌信息"""
    plate = models.CharField(max_length=50, unique=True)
    user = models.ForeignKey(DBUser, on_delete=models.CASCADE)
    register_time = models.DateTimeField(auto_now_add=True)


class DBPrice(models.Model):
    """定价策略"""
    _price = models.TextField(default=json.dumps([0.1 for _ in range(96)]))

    def query(self):
        query_ls = []
        price_ls = json.loads(self._price)[64:] + json.loads(self._price)[:64]
        begin_t = 0
        end_t = 0
        price_v = price_ls[0]
        for i in range(96):
            if (price_ls[i] == price_v):
                continue
            end_t = i
            p = {}
            p["price"] = price_v
            p["begin"] = f"{begin_t//4}:{(begin_t%4)*15}:00"
            if (end_t % 4 != 0):
                p["end"] = f"{end_t//4}:{(end_t%4)*15-1}:59"
            else:
                p["end"] = f"{end_t//4-1}:59:59"
            query_ls.append(p)
            begin_t = i
            price_v = price_ls[i]
        end_t = 96
        p = {}
        p["price"] = price_v
        p["begin"] = f"{begin_t//4}:{(begin_t%4)*15}:00"
        if (end_t % 4 != 0):
            p["end"] = f"{end_t//4}:{(end_t%4)*15-1}:59"
        else:
            p["end"] = f"{end_t//4-1}:59:59"
        query_ls.append(p)
        return query_ls

    def edit(self, price_str="[]"):
        price_str = price_str.replace("\'", "\"")
        try:
            price_ls = json.loads(self._price)[64:] + json.loads(self._price)[:64]
            for p in json.loads(price_str):
                begin_hour = int(p["begin"].split(":")[0])
                begin_min = int(p["begin"].split(":")[1])
                begin_sec = int(p["begin"].split(":")[2])
                end_hour = int(p["end"].split(":")[0])
                end_min = int(p["end"].split(":")[1])
                end_sec = int(p["end"].split(":")[2])
                price_v = float(p["price"])
                if (begin_hour < 0 or begin_hour > 23):
                    return False
                if (begin_min < 0 or begin_min > 59):
                    return False
                if (begin_sec < 0 or begin_sec > 59):
                    return False
                if (end_hour < 0 or end_hour > 23):
                    return False
                if (end_min < 0 or end_min > 59):
                    return False
                if (end_sec < 0 or end_sec > 59):
                    return False
                begin_t = (begin_hour * 3600 + begin_min * 60 + begin_sec + 1) // 900
                end_t = (end_hour * 3600 + end_min * 60 + end_sec + 1) // 900
                if (begin_t < end_t):
                    for i in range(begin_t, end_t):
                        price_ls[i] = price_v
                elif (begin_t == end_t):
                    price_ls[begin_t % 96] = price_v
                else:
                    for i in range(begin_t, 96):
                        price_ls[i] = price_v
                    for i in range(0, end_t):
                        price_ls[i] = price_v
            self._price = json.dumps(price_ls[32:]+price_ls[:32])
            self.save()
            return True
        except:
            pass
        return False

    def price(self):
        return json.loads(self._price)


class DBSpot(models.Model):
    """停车场车位"""
    spot = models.CharField(max_length=50, unique=True)


class DBMap(models.Model):
    """停车场元素布局向量"""
    item_type = models.CharField(max_length=50)
    spot = models.ForeignKey(DBSpot, on_delete=models.CASCADE, null=True)
    bx = models.FloatField()
    by = models.FloatField()
    ex = models.FloatField()
    ey = models.FloatField()


class DBOrder(models.Model):
    """订单信息"""
    plate = models.ForeignKey(DBPlateNumber, on_delete=models.CASCADE)
    user = models.ForeignKey(DBUser, on_delete=models.CASCADE)
    spot = models.ForeignKey(DBSpot, on_delete=models.CASCADE)
    status = models.IntegerField(default=0)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    duration = models.DurationField(default=timedelta(seconds=0))
    begin_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True)
    
    def save(self, *args, **kwargs):
        if self.end_time:
            time_difference = self.end_time - self.begin_time
            self.duration = time_difference
            price = DBPrice.objects.get().price()
            price_begin = self.begin_time.hour * 4 + self.begin_time.minute // 15
            price_cnt = (int(self.duration.total_seconds())-1) // 900 + 1
            self.amount = Decimal(0)
            for i in range(price_cnt):
                self.amount += round(Decimal(price[(price_begin+i)%96]), 2)
        super(DBOrder, self).save(*args, **kwargs)

class DBNotice(models.Model):
    title = models.CharField(max_length=50, unique=True)
    content = models.TextField()
    create_time = models.DateTimeField(auto_now_add=True)