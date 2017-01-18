from django.conf.urls import url

from user import views as user_views

app_name = 'user'
urlpatterns = [
    url(r'^$', user_views.user, name='user'),
    url(
        r'^change_password/$', user_views.change_password,
        name='change_password'),
    url(
        r'^change_password_done/$', user_views.change_password_done,
        name='password_reset_done'),
]
