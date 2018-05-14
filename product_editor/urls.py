"""URLs for the product_editor app."""

from django.urls import path

from product_editor import views

app_name = 'product_editor'


urlpatterns = [
    path(
        'basic_info/',
        views.BasicInfo.as_view(), name='basic_info'),
    path(
        'listing_options/',
        views.ListingOptions.as_view(),
        name='listing_options'),
    path(
        'unused_variations/',
        views.UnusedVariations.as_view(),
        name='unused_variations'),
    path(
        'variation_options/',
        views.VariationOptions.as_view(),
        name='variation_options'),
    path(
        'variation_info/',
        views.VariationInfo.as_view(),
        name='variation_info'),
    path(
        'variation_listing_options/',
        views.VariationListingOptions.as_view(),
        name='variation_listing_options'),
    path(
        'delete_product/',
        views.DeleteProductView.as_view(), name='delete_product'),
    path('finish_product/',
         views.FinishProduct.as_view(), name='finish'),
]
