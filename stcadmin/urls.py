"""stcadmin URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from user import views as user_views

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

admin.site.site_header = 'STC Stores Administration'

app_name = 'stcadmin'
urlpatterns = [
    path('admin/', admin.site.urls),
    path('user/', include('user.urls', namespace='user')),
    path('suppliers/', include('suppliers.urls', namespace='suppliers')),
    path('labelmaker/', include('labelmaker.urls', namespace='labelmaker')),
    path('epos/', include('epos.urls', namespace='epos')),
    path('reference/', include('reference.urls', namespace='reference')),
    path('inventory/', include('inventory.urls', namespace='inventory')),
    path('stock_check/', include('stock_check.urls', namespace='stock_check')),
    path(
        'price_calculator/',
        include('price_calculator.urls', namespace='price_calculator')),
    path(
        'print_audit/',
        include('print_audit.urls', namespace='print_audit')),
    path(
        'spring_manifest/',
        include('spring_manifest.urls', namespace='spring_manifest')),
    path(
        'profit_loss/',
        include('profit_loss.urls', namespace='profit_loss')),
    path('', include('home.urls', namespace='home')),
    path(
        'password_change_done/', user_views.change_password_done,
        name='password_change_done')
]

if settings.DEBUG:
    from django.conf.urls.static import static
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
