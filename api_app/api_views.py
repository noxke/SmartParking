from django.http import HttpResponse, HttpRequest
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.contrib.sessions.backends.db import SessionStore, UpdateError
import json

@csrf_exempt
def api_handler(request:HttpRequest, path=""):
    if (settings.SESSION_NAME in request.COOKIES):
        session_key = request.COOKIES[settings.SESSION_NAME]
        session = SessionStore(session_key)
    else:
        session = SessionStore()
    route = path.split(".")[0]
    method = path.split(".")[1]
    match route:
        case "user":
            from .user import User
            router = User(request, session, method)
            response = router.response
        case "plate":
            from .plate import Plate
            router = Plate(request, session, method)
            response = router.response
        case "order":
            from .order import Order
            router = Order(request, session, method)
            response = router.response
        case _:
            response = {"status": -1, "msg": "unknown api", "data": None}
    try:
        session.save()
    except UpdateError:
        pass
    session_key = session.session_key
    response = HttpResponse(json.dumps(response))
    response.set_cookie(settings.SESSION_NAME, session_key)
    return response