import json

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from .models import UserProfile


def _json_body(request):
    try:
        return json.loads(request.body.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return None


@require_POST
def api_login(request):
    data = _json_body(request)
    if data is None:
        return JsonResponse({"success": False, "error": "invalid_json"}, status=400)

    user = authenticate(request, username=data.get("email"), password=data.get("password"))
    if user is None:
        return JsonResponse({"success": False, "error": "invalid_credentials"}, status=401)

    login(request, user)
    return JsonResponse({"success": True})


@require_POST
def api_register(request):
    data = _json_body(request)
    if data is None:
        return JsonResponse({"success": False, "error": "invalid_json"}, status=400)
    if data.get("personal_data_consent") is not True:
        return JsonResponse({"success": False, "error": "personal_data_consent_required"}, status=400)

    name = (data.get("name") or "").strip()
    email = (data.get("email") or "").strip().lower()
    phone = (data.get("phone") or "").strip()
    address = (data.get("address") or "").strip()
    password = data.get("password") or ""

    if not name or not email or not phone or not password:
        return JsonResponse({"success": False, "error": "required_fields_missing"}, status=400)
    if User.objects.filter(username__iexact=email).exists():
        return JsonResponse({"success": False, "error": "user_exists"}, status=409)

    try:
        validate_password(password)
    except ValidationError:
        return JsonResponse({"success": False, "error": "weak_password"}, status=400)

    user = User.objects.create_user(username=email, email=email, password=password, first_name=name)
    profile, _ = UserProfile.objects.get_or_create(user=user)
    profile.phone = phone
    profile.address = address
    profile.save(update_fields=["phone", "address"])

    login(request, user)
    return JsonResponse({"success": True})


@require_POST
def api_logout(request):
    logout(request)
    return JsonResponse({"success": True})
