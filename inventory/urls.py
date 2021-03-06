"""URLs for the inventory app."""

from django.urls import path

from inventory import views

app_name = "inventory"

inventory_urlpatterns = [
    path("product_search/", views.ProductSearchView.as_view(), name="product_search"),
    path(
        "product_range/<int:range_id>/",
        views.ProductRangeView.as_view(),
        name="product_range",
    ),
    path(
        "locations/<int:range_id>/", views.LocationFormView.as_view(), name="locations"
    ),
    path("images/<int:range_id>/", views.ImageFormView.as_view(), name="images"),
    path("product/<int:product_id>/", views.ProductView.as_view(), name="product"),
    path(
        "descriptions/<int:range_id>/",
        views.DescriptionsView.as_view(),
        name="descriptions",
    ),
    path("sku_generator/", views.SKUGeneratorView.as_view(), name="sku_generator"),
    path(
        "print_barcodes/<int:range_id>/",
        views.PrintBarcodeLabels.as_view(),
        name="print_barcodes",
    ),
    path("barcode_pdf/", views.BarcodePDF.as_view(), name="barcode_pdf"),
    path("suppliers/suppliers", views.Suppliers.as_view(), name="suppliers"),
    path("suppliers/<int:pk>/", views.Supplier.as_view(), name="supplier"),
    path(
        "suppliers/create_supplier/",
        views.CreateSupplier.as_view(),
        name="create_supplier",
    ),
    path(
        "suppliers/create_contact/<int:supplier_pk>/",
        views.CreateSupplierContact.as_view(),
        name="create_supplier_contact",
    ),
    path(
        "suppliers/update_contact/<int:pk>/",
        views.UpdateSupplierContact.as_view(),
        name="update_supplier_contact",
    ),
    path(
        "suppliers/delete_contact/<int:pk>/",
        views.DeleteSupplierContact.as_view(),
        name="delete_supplier_contact",
    ),
    path(
        "toggle_supplier_active/<int:pk>/",
        views.ToggleSupplierActive.as_view(),
        name="toggle_supplier_active",
    ),
]

api_urlpatterns = [
    path(
        "get_stock_for_products/",
        views.GetStockForProductView.as_view(),
        name="get_stock_for_product",
    ),
    path("get_new_sku/", views.GetNewSKUView.as_view(), name="get_new_sku"),
    path(
        "get_new_range_sku/",
        views.GetNewRangeSKUView.as_view(),
        name="get_new_range_sku",
    ),
    path(
        "update_stock_level/",
        views.UpdateStockLevelView.as_view(),
        name="update_stock_level",
    ),
    path("set_image_order/", views.SetImageOrderView.as_view(), name="set_image_order"),
    path("delete_image/", views.DeleteImage.as_view(), name="delete_image"),
    path("search_hs_code/", views.SearchHSCode.as_view(), name="search_hs_code"),
    path(
        "search_product_name/",
        views.SearchProductName.as_view(),
        name="search_product_name",
    ),
    path(
        "search_product_sku/",
        views.SearchProductSKU.as_view(),
        name="search_product_sku",
    ),
]

urlpatterns = inventory_urlpatterns + api_urlpatterns
