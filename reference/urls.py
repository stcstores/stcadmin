from django.urls import path
from reference import views

app_name = 'reference'

urlpatterns = [
    path(
        'spring_services/', views.SpringServices.as_view(),
        name='spring_services'),
    path('', views.Index.as_view(), name='index'),
]
