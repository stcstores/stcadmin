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
from django.conf.urls import include, url
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from user import views as user_views

admin.site.site_header = 'STC Stores Administration'

app_name = 'stcadmin'
urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^user/', include('user.urls', namespace='user')),
    url(r'^suppliers/', include('suppliers.urls', namespace='suppliers')),
    url(r'^labelmaker/', include(
        'labelmaker.urls', namespace='labelmaker')),
    url(r'^photos/', include('photos.urls', namespace='photos')),
    url(r'^epos/', include('epos.urls', namespace='epos')),
    url(r'^reference/', include('reference.urls', namespace='reference')),
    url(r'^linnworks/', include('linnworks.urls', namespace='linnworks')),
    url(
        r'^cloud_commerce/',
        include('cloud_commerce.urls', namespace='cloud_commerce')),
    url(
        r'^cloud_commerce_api/',
        include('cloud_commerce_api.urls', namespace='cloud_commerce_api')),
    url(r'^', include('home.urls', namespace='home')),
    url(
        r'^password_change_done/', user_views.change_password_done,
        name='password_change_done')
]

if settings.DEBUG:
    from django.conf.urls.static import static
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
