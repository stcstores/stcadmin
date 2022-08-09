"""URLs for the channels app."""

from django.urls import path

from channels import views

app_name = "channels"
urlpatterns = [
    path("", views.Index.as_view(), name="index"),
    path(
        "shopify_products",
        views.ShopifyProducts.as_view(),
        name="shopify_products",
    ),
    path(
        "create_shopify_listing/<int:product_range_pk>/",
        views.CreateShopifyListing.as_view(),
        name="create_shopify_listing",
    ),
    path(
        "update_shopify_listing/<int:pk>/",
        views.UpdateShopifyListing.as_view(),
        name="update_shopify_listing",
    ),
]
