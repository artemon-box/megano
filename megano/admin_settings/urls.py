from django.urls import path

from .views import reset_all_cache, reset_cart_cache

app_name = "admin_settings"


urlpatterns = [
    path("reset_all_cache/", reset_all_cache, name="reset_all_cache"),
    path("reset_cart_cache/", reset_cart_cache, name="reset_cart_cache"),
]
