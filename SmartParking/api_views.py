from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import json

@csrf_exempt
def api_handler(request, path=None):
    status = {"status": -1, "msg": "unknown api", "data": None}
    return HttpResponse(json.dumps(status))