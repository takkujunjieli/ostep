import json
from functools import wraps

from django.http import JsonResponse


class Problem(Exception):
    def __init__(self, code, status=400):
        self.code, self.status = code, status


def endpoint(method):
    def decorate(function):
        @wraps(function)
        def wrapped(request, *args, **kwargs):
            if request.method != method:
                return JsonResponse({"error": "METHOD_NOT_ALLOWED"}, status=405)
            if not request.user.is_authenticated:
                return JsonResponse({"error": "LOGIN_REQUIRED"}, status=401)
            try:
                data = {}
                if method == "POST":
                    data = json.loads(request.body or b"{}")
                    if not isinstance(data, dict):
                        raise Problem("INVALID_JSON")
                return function(request, data, *args, **kwargs)
            except Problem as error:
                return JsonResponse({"error": error.code}, status=error.status)
            except (ValueError, UnicodeDecodeError):
                return JsonResponse({"error": "INVALID_INPUT"}, status=400)
        return wrapped
    return decorate


def text(value, maximum=500):
    if not isinstance(value, str) or not value.strip() or len(value.strip()) > maximum:
        raise Problem("INVALID_INPUT")
    return value.strip()


def positive_int(value):
    if type(value) is not int or not 0 < value <= 100000000:
        raise Problem("INVALID_INPUT")
    return value
