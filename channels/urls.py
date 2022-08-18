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
        "shopify/listing/<int:listing_pk>/",
        views.ShopifyListing.as_view(),
        name="shopify_listing",
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
    path(
        "upload_shopify_listing/",
        views.UploadShopifyListing.as_view(),
        name="upload_shopify_listing",
    ),
    path(
        "shopify_listing_status/<int:listing_pk>/",
        views.ShopifyListingStatus.as_view(),
        name="shopify_listing_status",
    ),
    path(
        "shopify_listing_active_status",
        views.ShopifyListingActiveStatus.as_view(),
        name="shopify_listing_active_status",
    ),
]
