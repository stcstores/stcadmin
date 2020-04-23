"""URLs for the fnac app."""

from django.urls import path

from fnac import views

app_name = "fnac"
urlpatterns = [
    path("", views.Index.as_view(), name="index"),
    path(
        "invalid_in_inventory/",
        views.InvalidInInventory.as_view(),
        name="invalid_in_inventory",
    ),
    path("translations/", views.Translations.as_view(), name="translations"),
    path(
        "translations_export/",
        views.TranslationsExport.as_view(),
        name="translations_export",
    ),
    path("shipping_comment/", views.ShippingComment.as_view(), name="shipping_comment"),
    path("created_products/", views.CreatedProducts.as_view(), name="created_products"),
    path(
        "missing_information/",
        views.MissingInformation.as_view(),
        name="missing_information",
    ),
    path(
        "missing_information/create_export/",
        views.CreateMissingInformationExport.as_view(),
        name="create_missing_information_export",
    ),
    path(
        "missing_information/export_status/",
        views.MissingInformationExportStatus.as_view(),
        name="missing_information_export_status",
    ),
    path(
        "inventory_update/start/",
        views.StartInventoryUpdate.as_view(),
        name="start_inventory_update",
    ),
    path(
        "inventory_update/status/",
        views.InventoryUpdateStatus.as_view(),
        name="inventory_update_status",
    ),
    path(
        "offer_update/create/",
        views.CreateOfferUpdate.as_view(),
        name="create_offer_update",
    ),
    path(
        "offer_update/status/",
        views.OfferUpdateStatus.as_view(),
        name="offer_update_status",
    ),
    path(
        "new_product_export/create/",
        views.CreateNewProductExport.as_view(),
        name="create_new_product_export",
    ),
    path(
        "new_product_export/status/",
        views.NewProductExportStatus.as_view(),
        name="new_product_export_status",
    ),
]
