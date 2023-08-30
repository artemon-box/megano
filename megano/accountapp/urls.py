from django.urls import path
from .views import RegistrationView, LoginView, LogoutView, password_reset, password_reset_confirm


urlpatterns = [
    path('registration/', RegistrationView.as_view(), name='registration_view'),
    path('login/', LoginView.as_view(), name='login_view'),
    path('logout/', LogoutView.as_view(), name='logout_view'),
    path('password-reset/', password_reset, name='password_reset_view'),
    path('password-reset-confirm/', password_reset_confirm, name='password_reset_confirm_view'),
]
