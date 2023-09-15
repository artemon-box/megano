from django.contrib import messages
from django.core.cache import cache
from django.shortcuts import redirect


def reset_all_cache(request):
    # Сброс всего кэша
    try:
        cache.clear()
        messages.success(request, 'Кеш был успешно сброшен')
    except Exception as e:
        messages.error(request, 'При сбросе кэша произошла ошибка')
    return redirect(request.META.get('HTTP_REFERER'))
