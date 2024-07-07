from django.apps import AppConfig
from django.db.utils import ProgrammingError

class PkdbConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'PKDB'

    def ready(self):
        import sys
        from pathlib import Path
        if ("runserver_plus" not in sys.argv):
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
        from PKDB.models import DBOrder
        DBOrder.objects.all().delete()

        # 新建管理员用户
        import os
        from django.contrib.auth.hashers import make_password
        admin = DBAdmin(name=os.environ.get('MGR_NAME'), password=make_password(os.environ.get('MGR_PASSWD')))
        admin.save()

        # 测试数据新增
        import random
        import string
        from django.utils import timezone
        from datetime import timedelta
        for i in range(100):
            name = ''.join(random.choice(string.ascii_letters + string.digits ) for _ in range(random.randint(5, 10)))
            balance = random.randint(5, 1000)
            user = DBUser(name=name, password=make_password("passwd"), balance=balance, phone=f"{10000+i}", email=f"{name}@123.com")
            user.last_login = timezone.now() + timedelta(seconds=random.randint(10000, 400000))
            user.save()
            for j in range(random.randint(0, 5)):
                plate = DBPlateNumber(plate=f"A_{name[:4]}_{j}", user=user)
                plate.save()
                for k in range(0, 10):
                    price = random.randint(1, 5)
                    order = DBOrder(plate=plate, user=user, price=price)
                    order.save()
                    if (random.randint(0, 1)== 1):
                        order.end_time = timezone.now() + timedelta(seconds=random.randint(500, 50000))
                        order.save()

