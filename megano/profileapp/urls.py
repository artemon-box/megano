from django.urls import path
from .views import ProfileAvatarView, ProfileView, AccountView

app_name = "profileapp"

urlpatterns = [
    path('profile/avatar/', ProfileAvatarView.as_view(), name='profile_avatar'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('', AccountView.as_view(), name='account'),
]