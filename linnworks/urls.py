from django.conf.urls import url

from linnworks import views as linnworks_views

app_name = 'linnworks'

urlpatterns = [
    url(r'^$', linnworks_views.index, name='index'),
    url(r'^manifest/$', linnworks_views.manifest, name='manifest'),
    url(
        r'^cancel_consignment$', linnworks_views.cancel_consignment,
        name='cancel_consignment'),
    url(
        r'^sku_converter/$', linnworks_views.sku_converter,
        name='sku_converter'),
]
