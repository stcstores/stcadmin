"""URLs for the home app."""

from django.contrib.auth import views as auth_views
from django.urls import path
from django.views.generic import TemplateView

from home import views

app_name = 'home'
urlpatterns = [
    path('', views.Index.as_view(), name='index'),
    path(
        'login/', auth_views.login,
        {'template_name': 'home/login.html'}, name='login_user'),
    path(
        'logout/', auth_views.logout, {'next_page': 'home:login_user'},
        name='logout_user'),
    path('robots.txt', TemplateView.as_view(
        template_name='home/robots.txt', content_type='text/plain')),
]
