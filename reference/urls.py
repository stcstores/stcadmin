from django.conf.urls import url
from reference import views

app_name = 'reference'

urlpatterns = [
    url(r'^$', views.Index.as_view(), name='index'),
]
