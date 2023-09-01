from django.urls import path
from .views import RegistrationView, LoginView, LogoutView, PasswordResetView, PasswordResetConfirm


urlpatterns = [
    path('registration/', RegistrationView.as_view(), name='registration_view'),
    path('login/', LoginView.as_view(), name='login_view'),
    path('logout/', LogoutView.as_view(), name='logout_view'),
    path('password-reset/', PasswordResetView.as_view(), name='password_reset_view'),
    path('password-reset-confirm/', PasswordResetConfirm.as_view(), name='password_reset_confirm_view'),
]
