"""stcadmin URL Configuration."""

import debug_toolbar
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.static import serve

from home import views as home_views

admin.site.site_header = "STC Stores Administration"


app_name = "stcadmin"
urlpatterns = [
    path("admin/", admin.site.urls),
    path("select2/", include("django_select2.urls")),
    path("summernote/", include("django_summernote.urls")),
    path("labelmaker/", include("labelmaker.urls", namespace="labelmaker")),
    path("inventory/", include("inventory.urls", namespace="inventory")),
    path(
        "price_calculator/",
        include("price_calculator.urls", namespace="price_calculator"),
    ),
    path("orders/", include("orders.urls", namespace="orders")),
    path("channels/", include("channels.urls", namespace="channels")),
    path("reports/", include("reports.urls", namespace="reports")),
    path("fba/", include("fba.urls", namespace="fba")),
    path("purchases/", include("purchases.urls", namespace="purchases")),
    path("linnworks/", include("linnworks.urls", namespace="linnworks")),
    path("restock/", include("restock.urls", namespace="restock")),
    path("hours/", include("hours.urls", namespace="hours")),
    path("logs/", include("logs.urls", namespace="logs")),
    path("", include("home.urls", namespace="home")),
    path(
        "password_change_done/",
        home_views.ChangePasswordDone.as_view(),
        name="password_change_done",
    ),
    path("docs/<str:path>", serve, {"document_root": settings.DOCS_ROOT}),
    path("docs/_static/<str:path>", serve, {"document_root": settings.DOCS_ROOT}),
]


urlpatterns = [path("__debug__/", include(debug_toolbar.urls))] + urlpatterns
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
