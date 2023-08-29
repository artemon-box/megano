from django.urls import path
from . import views


app_name = "shopapp"

urlpatterns = [
    path('compare/', views.comparison_of_products, name='compare_list'),
    path('compare/add/<int:product_id>/', views.add_to_comparison, name='compare_add'),
    path('compare/remove/<int:product_id>/', views.remove_from_comparison, name='compare_remove'),
]
