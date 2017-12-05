from django.conf.urls import url
from reference import views

app_name = 'reference'

urlpatterns = [
    url(
        r'^spring_services$', views.SpringServices.as_view(),
        name='spring_services'),
    url(r'^$', views.Index.as_view(), name='index'),
]
