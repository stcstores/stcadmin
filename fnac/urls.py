"""URLs for the fnac app."""

from django.urls import path

from fnac import views

app_name = "fnac"
urlpatterns = [
    path("", views.Index.as_view(), name="index"),
    path(
        "missing_inventory_info/",
        views.MissingInventoryInfo.as_view(),
        name="missing_inventory_info",
    ),
    path(
        "missing_price_size/",
        views.MissingPriceSize.as_view(),
        name="missing_price_size",
    ),
    path("missing_category/", views.MissingCategory.as_view(), name="missing_category"),
    path("translations/", views.Translations.as_view(), name="translations"),
    path(
        "translations_export/",
        views.TranslationsExport.as_view(),
        name="translations_export",
    ),
    path("new_product_file/", views.NewProductFile.as_view(), name="new_product_file"),
]
