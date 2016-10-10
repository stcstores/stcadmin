from django.conf.urls import url

from photos import views

app_name = 'photos'
urlpatterns = [
    url(r'^api/photo_list/', views.api_photo_list, name='api_photo_list'),
    url(
        r'^api/photo_delete/', views.api_photo_delete,
        name='api_photo_delete'),
    url(r'^$', views.index, name='index'),
]
