from django.urls import path
from reference import views

app_name = 'reference'

urlpatterns = [
    path('package_types/', views.PackageTypes.as_view(), name='package_types'),
    path(
        'product_creation', views.ProductCreation.as_view(),
        name='product_creation'),
    path(
        'spring_services/', views.SpringServices.as_view(),
        name='spring_services'),
    path('', views.Index.as_view(), name='index'),
]
