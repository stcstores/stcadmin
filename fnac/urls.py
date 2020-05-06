"""URLs for the fnac app."""

from django.urls import path

from fnac import views

app_name = "fnac"
urlpatterns = [
    path("", views.Index.as_view(), name="index"),
    path("update_offers/", views.UpdateOffers.as_view(), name="update_offers"),
    path("create_products/", views.CreateProducts.as_view(), name="create_products"),
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
        "missing_information/start_import/",
        views.StartMissingInformationImport.as_view(),
        name="start_missing_information_import",
    ),
    path(
        "missing_information/import_status/",
        views.MissingInformationImportStatus.as_view(),
        name="missing_information_import_status",
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
    path(
        "add_created_products/",
        views.AddCreatedProducts.as_view(),
        name="add_created_products",
    ),
    path(
        "add_created_products/mirakl_product_file_status/",
        views.MiraklProductFileImportStatus.as_view(),
        name="mirakl_product_import_status",
    ),
    path(
        "add_created_products/start_mirakl_product_file_import/",
        views.StartMiraklProductFileImport.as_view(),
        name="start_mirakl_product_file_import",
    ),
]
