from django.apps import AppConfig
from django.db.utils import ProgrammingError

class PkdbConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'PKDB'

    def ready(self):
        import sys
        from pathlib import Path
        if ("runserver" not in sys.argv):
            return
        BASE_DIR = Path(__file__).resolve().parent.parent
        lock_file = BASE_DIR.joinpath("install.lock")
        if (not lock_file.exists()):
            self.db_init()
            lock_file.touch()

    def db_init(self):
        # 清空表
        from PKDB.models import DBAdmin
        DBAdmin.objects.all().delete()
        from PKDB.models import DBUser
        DBUser.objects.all().delete()
        from PKDB.models import DBPlateNumber
        DBPlateNumber.objects.all().delete()
        from PKDB.models import DBPrice
        DBPrice.objects.all().delete()
        from PKDB.models import DBSpot
        DBSpot.objects.all().delete()
        from PKDB.models import DBMap
        DBMap.objects.all().delete()
        from PKDB.models import DBOrder
        DBOrder.objects.all().delete()
        from PKDB.models import DBNotice
        DBNotice.objects.all().delete()

        # 新建管理员用户
        import os
        from django.contrib.auth.hashers import make_password
        admin = DBAdmin(name=os.environ.get('MGR_NAME'), password=make_password(os.environ.get('MGR_PASSWD')))
        admin.save()

        # 新建价格表
        price = DBPrice()
        price.save()

        # 测试数据新增
        # 生成车位
        spots = []
        for i in range(100):
            spot = DBSpot(spot=f"S_{1000+i}")
            spot.save()
            spots.append(spot)

        import random
        import string
        from django.utils import timezone
        from datetime import timedelta
        for i in range(100):
            # 生成用户
            name = ''.join(random.choice(string.ascii_uppercase) for _ in range(random.randint(5, 10)))
            balance = random.randint(5, 1000)
            user = DBUser(name=name, password=make_password("passwd"), balance=balance, phone=f"{10000+i}", email=f"{name}@123.com")
            user.last_login = timezone.now() + timedelta(seconds=random.randint(10000, 400000))
            user.save()
            for j in range(random.randint(0, 5)):
                # 生成车牌
                plate = DBPlateNumber(plate=f"{random.choice(string.ascii_uppercase)}_{name[:4]}{j}", user=user)
                plate.save()
                for k in range(0, 10):
                    # 生成订单
                    order = DBOrder(plate=plate, user=user, spot=spots[random.randint(0, 99)], status = random.randint(0, 1))
                    order.save()
                    if (random.randint(0, 1)== 1):
                        order.end_time = timezone.now() + timedelta(seconds=random.randint(500, 50000))
                        order.status = random.randint(2, 3)
                        order.save()

