from django.urls import path
from shopapp.views import catalog_list

app_name = "shopapp"

urlpatterns = [
    path('catalog/', catalog_list, name='catalog_list'),
]
