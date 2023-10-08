from django.contrib import messages
from django.core.cache import cache
from django.shortcuts import redirect


def reset_all_cache(request):
    # Сброс всего кэша
    try:
        cache.clear()
        messages.success(request, "Весь кэш сайта был успешно сброшен")
    except KeyError:
        messages.error(request, "Такой ключ не найден")
    except Exception as e:
        messages.error(request, "При сбросе кэша произошла ошибка", str(e))
    return redirect(request.META.get("HTTP_REFERER"))


def reset_cart_cache(request):
    # сброс кэша корзины
    try:
        cache.delete("cart_items")
        messages.success(request, "Кэш корзины успешно сброшен")
    except KeyError:
        messages.error(request, "Такой ключ не найден")
    except Exception as e:
        messages.error(request, "При сбросе кэша произошла ошибка", str(e))
    return redirect(request.META.get("HTTP_REFERER"))
