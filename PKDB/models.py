from django.db import models
from datetime import timedelta
from decimal import Decimal

# Create your models here.
class DBAdmin(models.Model):
    name = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=128)
    register_time = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(null=True)

class DBUser(models.Model):
    name = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=128)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    phone = models.CharField(max_length=128, null=True)
    email = models.EmailField(max_length=128, null=True)
    register_time = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(null=True)

class DBPlateNumber(models.Model):
    plate = models.CharField(max_length=50, unique=True)
    user = models.ForeignKey(DBUser, on_delete=models.CASCADE)
    register_time = models.DateTimeField(auto_now_add=True)


class DBOrder(models.Model):
    plate = models.ForeignKey(DBPlateNumber, on_delete=models.CASCADE)
    user = models.ForeignKey(DBUser, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    duration = models.DurationField(default=timedelta(seconds=0))
    begin_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True)
    
    def save(self, *args, **kwargs):
        if self.end_time:
            time_difference = self.end_time - self.begin_time
            self.duration = time_difference
            total_min = self.duration.total_seconds() // 900  # 按15分钟计算
            if self.duration.total_seconds() % 900 > 0:  # 不足15分钟按15分钟计算
                total_min += 1
            self.amount = self.price * Decimal(str(total_min))
        super(DBOrder, self).save(*args, **kwargs)