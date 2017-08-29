from django.conf.urls import url
from django.views.generic import TemplateView

from . import views
from django.contrib.auth import views as auth_views

app_name = 'home'
urlpatterns = [
    url(r'^$', views.Index.as_view(), name='index'),
    url(
        r'^login/$', auth_views.login,
        {'template_name': 'home/login.html'}, name='login_user'),
    url(
        r'^logout/$', auth_views.logout, {'next_page': 'home:login_user'},
        name='logout_user'),
    url(r'^robots.txt$', TemplateView.as_view(
        template_name='home/robots.txt', content_type='text/plain')),
]
