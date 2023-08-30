from django.urls import path

from shopapp import views

app_name = "shopapp"

urlpatterns = [
    path('', views.test_base_template, name='test_base_template'),
    path('registr/', views.test_registr_template, name='test_registr_template'),
]
