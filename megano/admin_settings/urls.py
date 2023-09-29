from django.urls import path

from .views import reset_all_cache

app_name = "admin_settings"


urlpatterns = [
    path("reset_all_cache/", reset_all_cache, name="reset_all_cache"),
]
