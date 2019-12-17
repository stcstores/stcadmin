"""stcadmin URL Configuration."""

from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from django.views.static import serve

from user import views as user_views

admin.site.site_header = "STC Stores Administration"


app_name = "stcadmin"
urlpatterns = [
    path("admin/", admin.site.urls),
    path("user/", include("user.urls", namespace="user")),
    path("labelmaker/", include("labelmaker.urls", namespace="labelmaker")),
    path("reference/", include("reference.urls", namespace="reference")),
    path("inventory/", include("inventory.urls", namespace="inventory")),
    path("stock_check/", include("stock_check.urls", namespace="stock_check")),
    path("product_editor/", include("product_editor.urls", namespace="product_editor")),
    path("validation/", include("validation.urls", namespace="validation")),
    path(
        "price_calculator/",
        include("price_calculator.urls", namespace="price_calculator"),
    ),
    path("print_audit/", include("print_audit.urls", namespace="print_audit")),
    path(
        "spring_manifest/", include("spring_manifest.urls", namespace="spring_manifest")
    ),
    path("profit_loss/", include("profit_loss.urls", namespace="profit_loss")),
    path("epos/", include("epos.urls", namespace="epos")),
    path("feedback/", include("feedback.urls", namespace="feedback")),
    path("", include("home.urls", namespace="home")),
    path(
        "password_change_done/",
        user_views.ChangePasswordDone.as_view(),
        name="password_change_done",
    ),
    path("docs/<str:path>", serve, {"document_root": settings.DOCS_ROOT}),
    path("docs/_static/<str:path>", serve, {"document_root": settings.DOCS_ROOT}),
]

if settings.DEBUG:
    from django.conf.urls.static import static
    import debug_toolbar

    urlpatterns = [path("__debug__/", include(debug_toolbar.urls))] + urlpatterns
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
