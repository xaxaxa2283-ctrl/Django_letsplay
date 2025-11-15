# main/views_auth.py
import json
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import UserProfile

@csrf_exempt
def api_login(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'invalid_json'}, status=400)

        email = data.get('email')
        password = data.get('password')

        # Аутентификация по email
        user = authenticate(request, username=email, password=password)

        if user is not None:
            login(request, user)
            return JsonResponse({'success': True})
        else:
            # ⚠️ Возвращаем код ошибки, который твой JS ожидает:
            return JsonResponse({'success': False, 'error': 'invalid_credentials'}, status=401)

    return JsonResponse({'error': 'method_not_allowed'}, status=405)


@csrf_exempt
def api_register(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'invalid_json'}, status=400)

        name = data.get('name')
        email = data.get('email')
        password = data.get('password')
        phone = data.get('phone')
        address = data.get('address')

        # Проверка на существующего пользователя
        if User.objects.filter(username=email).exists():
            return JsonResponse({'success': False, 'error': 'user_exists'}, status=409)

        # Создаём нового пользователя
        user = User.objects.create_user(username=email, email=email, password=password, first_name=name)
        user.save()

        # Если у тебя есть модель профиля — создаём профиль
        profile = user.profile
        profile.phone = phone
        profile.address = address
        profile.save()

        login(request, user)
        return JsonResponse({'success': True})

    return JsonResponse({'error': 'method_not_allowed'}, status=405)


def api_logout(request):
    logout(request)
    return JsonResponse({'success': True})
