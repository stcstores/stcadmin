"""URLs for the home app."""

from django.contrib.auth import views as auth_views
from django.urls import path
from django.views.generic import TemplateView

from home import views

app_name = "home"
urlpatterns = [
    path("", views.Index.as_view(), name="index"),
    path(
        "login/",
        auth_views.LoginView.as_view(template_name="home/login.html"),
        name="login_user",
    ),
    path(
        "logout/",
        auth_views.LogoutView.as_view(next_page="home:login_user"),
        name="logout_user",
    ),
    path(
        "robots.txt",
        TemplateView.as_view(
            template_name="home/robots.txt", content_type="text/plain"
        ),
    ),
    path("monitor/", views.DisplayMonitor.as_view(), name="monitor"),
    path("version/", views.Version.as_view(), name="version"),
    path("user/", views.User.as_view(), name="user"),
    path("change_password/", views.ChangePassword.as_view(), name="change_password"),
    path(
        "password_change_done/",
        views.ChangePasswordDone.as_view(),
        name="password_change_done",
    ),
]
