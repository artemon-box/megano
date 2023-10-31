from django.urls import path

from .views import AccountView, HistoryOrdersView, ProfileAvatarView, ProfileView

app_name = "profileapp"

urlpatterns = [
    path("accounts/profile/avatar/", ProfileAvatarView.as_view(), name="profile_avatar"),
    path("accounts/profile/", ProfileView.as_view(), name="profile"),
    path("accounts/", AccountView.as_view(), name="account"),
    path("orders/history-order/<int:order_id>/", HistoryOrdersView.as_view(), name="historyorder_id"),
    path("orders/history-order/", HistoryOrdersView.as_view(), name="historyorder"),
]
