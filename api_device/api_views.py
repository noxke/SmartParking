from django.http import HttpResponse, HttpRequest
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import json

@csrf_exempt
def api_handler(request:HttpRequest, path=""):
    route = path.split(".")[0]
    method = path.split(".")[1]
    match route:
        case "huawei-iot":
            from .huawei_iot import HuaweiIOT
            router = HuaweiIOT(request, method)
            response = router.response
        case _:
            response = {"status": -1, "msg": "unknown api", "data": None}
    return HttpResponse(json.dumps(response))