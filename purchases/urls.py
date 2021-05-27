"""URLs for the purchases app."""

from django.urls import path

from purchases import views

app_name = "purchases"

urlpatterns = [
    path("purchase/", views.Purchase.as_view(), name="purchase"),
    path("view_purchases/", views.ViewPurchases.as_view(), name="view_purchases"),
    path("manage_purchases/", views.ManagePurchases.as_view(), name="manage_purchases"),
    path("from_stock/", views.PurchaseFromStock.as_view(), name="from_stock"),
    path("from_shop/", views.PurchaseFromShop.as_view(), name="from_shop"),
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
    path(
        "mark_purchase_cancelled/",
        views.MarkOrderCancelled.as_view(),
        name="mark_purchase_cancelled",
    ),
    path("shipping_price/", views.GetShippingPrice.as_view(), name="shipping_price"),
    path("purchase_note", views.PurchaseNote.as_view(), name="purchase_note"),
]
