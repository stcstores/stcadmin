from django.conf.urls import url
from django.views.generic import TemplateView

from . import views

app_name = 'home'
urlpatterns = [
    url(r'^robots.txt$', TemplateView.as_view(
        template_name='home/robots.txt', content_type='text/plain')),
    url(r'^login/$', views.login_user, name='login_user'),
    url(r'^logout/$', views.logout_user, name='logout_user'),
    url(
        r'^$', views.index,
        name='index'),
]
