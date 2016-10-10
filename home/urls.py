from django.conf.urls import url

from home import views

app_name = 'home'
urlpatterns = [
    url(r'^login/$', views.login_user, name='login_user'),
    url(r'^logout/$', views.logout_user, name='logout_user'),
    url(
        r'^$', views.index,
        name='index'),
]
