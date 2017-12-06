from django.urls import path
from inventory import views

app_name = 'inventory'

inventory_urlpatterns = [
    path(
        'product_search/',
        views.ProductSearchView.as_view(), name='product_search'),
    path(
        'product_range/<int:range_id>/',
        views.ProductRangeView.as_view(), name='product_range'),
    path(
        'locations/<int:range_id>/',
        views.LocationFormView.as_view(), name='locations'),
    path(
        'variations/<int:range_id>/',
        views.VariationsFormView.as_view(), name='variations'),
    path(
        'images/<int:range_id>/',
        views.ImageFormView.as_view(), name='images'),
    path(
        'product/<int:product_id>/',
        views.ProductView.as_view(), name='product'),
    path(
        'descriptions/<int:range_id>/',
        views.DescriptionsView.as_view(), name='descriptions'),
    path(
        'sku_generator/',
        views.SKUGeneratorView.as_view(), name='sku_generator'),
    path(
        'delete_stcadmin_image/<int:image_id>/',
        views.DeleteSTCAdminImage.as_view(), name='delete_stcadmin_image'),
    path(
        'print_barcodes/<int:range_id>/',
        views.PrintBarcodeLabels.as_view(), name='print_barcodes'),
    path(
        'barcode_pdf/',
        views.BarcodePDF.as_view(), name='barcode_pdf'),
]

new_product_urlpatterns = [
    path(
        'new_product/',
        views.NewProductView.as_view(), name='new_product'),
    path(
        'new_single_product/',
        views.NewSingleProductView.as_view(), name='new_single_product'),
    path(
        'new_variation_product/',
        views.VariationFormWizardView.as_view(), name='new_variation_product'),

]

api_urlpatterns = [
    path(
        'get_stock_for_products/',
        views.GetStockForProductView.as_view(), name='get_stock_for_product'),
    path(
        'get_new_sku/',
        views.GetNewSKUView.as_view(), name='get_new_sku'),
    path(
        'get_new_range_sku/',
        views.GetNewRangeSKUView.as_view(), name='get_new_range_sku'),
    path(
        'update_stock_level/',
        views.UpdateStockLevelView.as_view(), name='update_stock_level'),
    path(
        'set_image_order/',
        views.SetImageOrderView.as_view(), name='set_image_order'),
    path(
        'delete_image/',
        views.DeleteImage.as_view(), name='delete_image'),
]

urlpatterns = inventory_urlpatterns + new_product_urlpatterns + api_urlpatterns
