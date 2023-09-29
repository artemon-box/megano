from django.urls import path

from .views import (
    LoginView,
    LogoutView,
    PasswordResetConfirm,
    PasswordResetView,
    RegistrationView,
)

app_name = "accountapp"

urlpatterns = [
    path('registration/', RegistrationView.as_view(), name='registration'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('password-reset/', PasswordResetView.as_view(), name='password_reset'),
    path('password-reset-confirm/', PasswordResetConfirm.as_view(), name='password_reset_confirm'),
]
