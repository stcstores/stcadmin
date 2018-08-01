"""URL patterns for the User app."""

from user import views as user_views

from django.urls import path

app_name = "user"
urlpatterns = [
    path("", user_views.User.as_view(), name="user"),
    path(
        "change_password/", user_views.ChangePassword.as_view(), name="change_password"
    ),
    path(
        "change_password_done/",
        user_views.ChangePasswordDone.as_view(),
        name="password_reset_done",
    ),
]
