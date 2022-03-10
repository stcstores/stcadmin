"""URLs for the inventory app."""

from django.urls import path

from inventory import views

app_name = "inventory"

inventory_urlpatterns = [
    path("product_search/", views.ProductSearchView.as_view(), name="product_search"),
    path(
        "product_range/<int:range_pk>/",
        views.ProductRangeView.as_view(),
        name="product_range",
    ),
    path(
        "locations/<int:range_pk>/", views.LocationFormView.as_view(), name="locations"
    ),
    path("images/<int:range_pk>/", views.ImageFormView.as_view(), name="images"),
    path("product/<int:product_pk>/", views.ProductView.as_view(), name="product"),
    path(
        "descriptions/<int:range_pk>/",
        views.DescriptionsView.as_view(),
        name="descriptions",
    ),
    path("sku_generator/", views.SKUGeneratorView.as_view(), name="sku_generator"),
    path(
        "product_order/<int:range_pk>/",
        views.ProductOrderView.as_view(),
        name="product_order",
    ),
    path(
        "print_barcodes/<int:range_pk>/",
        views.PrintBarcodeLabels.as_view(),
        name="print_barcodes",
    ),
    path("barcode_pdf/", views.BarcodePDF.as_view(), name="barcode_pdf"),
    path("suppliers/suppliers/", views.Suppliers.as_view(), name="suppliers"),
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
    path("get_new_sku/", views.GetNewSKUView.as_view(), name="get_new_sku"),
    path(
        "get_new_range_sku/",
        views.GetNewRangeSKUView.as_view(),
        name="get_new_range_sku",
    ),
    path("get_stock_level/", views.GetStockLevelView.as_view(), name="get_stock_level"),
    path(
        "update_stock_level/",
        views.UpdateStockLevelView.as_view(),
        name="update_stock_level",
    ),
    path("set_image_order/", views.SetImageOrderView.as_view(), name="set_image_order"),
    path("delete_image/", views.DeleteImage.as_view(), name="delete_image"),
]

product_editor_patterns = [
    path(
        "start_new_product/", views.StartNewProduct.as_view(), name="start_new_product"
    ),
    path(
        "resume_editing_product/<int:range_pk>/",
        views.ResumeEditingProduct.as_view(),
        name="resume_editing_product",
    ),
    path(
        "edit_new_product/<int:range_pk>/",
        views.EditNewProduct.as_view(),
        name="edit_new_product",
    ),
    path(
        "edit_product/<int:range_pk>/", views.EditProduct.as_view(), name="edit_product"
    ),
    path(
        "edit_variations/<int:range_pk>/",
        views.EditVariations.as_view(),
        name="edit_variations",
    ),
    path("continue/", views.Continue.as_view(), name="continue"),
    path(
        "range_form/<int:edit_ID>/",
        views.EditRangeDetails.as_view(),
        name="range_form",
    ),
    path(
        "add_dropdown/<int:edit_ID>/", views.AddDropdown.as_view(), name="add_dropdown"
    ),
    path(
        "add_listing_option/<int:edit_ID>/",
        views.AddListingOption.as_view(),
        name="add_listing_option",
    ),
    path(
        "set_product_option_values/<int:edit_ID>/",
        views.SetProductOptionValues.as_view(),
        name="set_product_option_values",
    ),
    path(
        "add_product_option_values/<int:edit_ID>/<int:product_option_ID>/",
        views.AddProductOptionValues.as_view(),
        name="add_product_option_values",
    ),
    path(
        "remove_product_option_value/<int:edit_ID>/<int:option_value_ID>/",
        views.RemoveProductOptionValue.as_view(),
        name="remove_product_option_value",
    ),
    path(
        "edit_variation/<int:edit_ID>/<int:product_ID>/",
        views.EditVariation.as_view(),
        name="edit_variation",
    ),
    path(
        "create_initial_variation/<int:range_pk>/",
        views.CreateInitialVariation.as_view(),
        name="create_initial_variation",
    ),
    path(
        "edit_all_variations/<int:range_pk>/",
        views.EditAllVariations.as_view(),
        name="edit_all_variations",
    ),
    path(
        "create_variation/<int:edit_ID>/",
        views.CreateVariation.as_view(),
        name="create_variation",
    ),
    path(
        "delete_variation/<int:edit_ID>/<int:product_ID>/",
        views.DeleteVariation.as_view(),
        name="delete_variation",
    ),
    path(
        "discard_new_range/<int:range_pk>/",
        views.DiscardNewRange.as_view(),
        name="discard_new_range",
    ),
    path(
        "remove_dowpdown/<int:edit_ID>/<int:product_option_ID>/",
        views.RemoveDropdown.as_view(),
        name="remove_dropdown",
    ),
    path(
        "complete_new_product/<int:range_pk>/",
        views.CompleteNewProduct.as_view(),
        name="complete_new_product",
    ),
    path(
        "setup_variations/<int:range_pk>/",
        views.SetupVariations.as_view(),
        name="setup_variations",
    ),
]

urlpatterns = inventory_urlpatterns + api_urlpatterns + product_editor_patterns
