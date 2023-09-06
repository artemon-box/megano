from django.urls import path
from .views import ProfileAvatarView, ProfileView, AccountView


urlpatterns = [
    path('profile/avatar/', ProfileAvatarView.as_view(), name='profile_avatar_view'),
    path('profile/', ProfileView.as_view(), name='profile_view'),
    path('', AccountView.as_view(), name='account_view'),
]