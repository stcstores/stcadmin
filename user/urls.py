from user import views as user_views

from django.urls import path

app_name = 'user'
urlpatterns = [
    path('', user_views.user, name='user'),
    path(
        'change_password/', user_views.change_password,
        name='change_password'),
    path(
        'change_password_done/', user_views.change_password_done,
        name='password_reset_done'),
]
