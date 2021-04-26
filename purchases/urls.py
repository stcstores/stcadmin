"""URLs for the purchases app."""

from django.urls import path

from purchases import views

app_name = "purchases"

urlpatterns = [
    path("purchase/", views.Purchase.as_view(), name="purchase"),
    path("manage/", views.Manage.as_view(), name="manage"),
    path("from_stock/", views.PurchaseFromStock.as_view(), name="from_stock"),
    path("shipping/", views.PurchaseShipping.as_view(), name="shipping"),
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
    path(
        "purchase_price/",
        views.ProductPurchasePrice.as_view(),
        name="product_purchase_price",
    ),
    path("manage_purchases/", views.ManagePurchases.as_view(), name="manage_purchases"),
    path(
        "mark_purchase_paid/", views.MarkOrderPaid.as_view(), name="mark_purchase_paid"
    ),
    path(
        "mark_purchase_cancelled/",
        views.MarkOrderCancelled.as_view(),
        name="mark_purchase_cancelled",
    ),
    path("shipping_price/", views.GetShippingPrice.as_view(), name="shipping_price"),
]
