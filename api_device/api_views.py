from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import json

@csrf_exempt
def api_handler(request, path=None):
    response = {"status": -1, "msg": "unknown api", "data": None}
    return HttpResponse(json.dumps(response))