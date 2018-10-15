"""URLs for the product_editor app."""

from django.urls import path
from product_editor import views

app_name = "product_editor"


urlpatterns = [
    path("basic_info/", views.NewBasicInfo.as_view(), name="basic_info"),
    path(
        "basic_info/<int:range_id>/", views.EditBasicInfo.as_view(), name="basic_info"
    ),
    path("product_info/", views.NewProductInfo.as_view(), name="product_info"),
    path(
        "product_info/<int:range_id>/",
        views.EditProductInfo.as_view(),
        name="product_info",
    ),
    path("listing_options/", views.NewListingOptions.as_view(), name="listing_options"),
    path(
        "listing_options/<int:range_id>/",
        views.EditListingOptions.as_view(),
        name="listing_options",
    ),
    path(
        "variation_options/",
        views.NewVariationOptions.as_view(),
        name="variation_options",
    ),
    path(
        "variation_options/<int:range_id>/",
        views.EditVariationOptions.as_view(),
        name="variation_options",
    ),
    path(
        "unused_variations/",
        views.NewUnusedVariations.as_view(),
        name="unused_variations",
    ),
    path(
        "unused_variations/<int:range_id>/",
        views.EditUnusedVariations.as_view(),
        name="unused_variations",
    ),
    path("variation_info/", views.NewVariationInfo.as_view(), name="variation_info"),
    path(
        "variation_info/<int:range_id>/",
        views.EditVariationInfo.as_view(),
        name="variation_info",
    ),
    path(
        "variation_listing_options/",
        views.NewVariationListingOptions.as_view(),
        name="variation_listing_options",
    ),
    path(
        "variation_listing_options/<int:range_id>/",
        views.EditVariationListingOptions.as_view(),
        name="variation_listing_options",
    ),
    path("clear_product/", views.ClearNewProduct.as_view(), name="clear_product"),
    path(
        "clear_product/<int:range_id>",
        views.ClearEditedProduct.as_view(),
        name="clear_product",
    ),
    path("finish_product/", views.FinishNewProduct.as_view(), name="finish"),
    path(
        "finish_product/<int:range_id>/",
        views.FinishEditProduct.as_view(),
        name="finish",
    ),
]
