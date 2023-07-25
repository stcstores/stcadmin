"""URLs for the purchases app."""

from django.urls import path

from purchases import views

app_name = "purchases"
urlpatterns = [
    path("", views.ProductSearch.as_view(), name="product_search"),
    path(
        "product_search_results",
        views.ProductSearchResults.as_view(),
        name="product_search_results",
    ),
    path(
        "create_purchase/<int:product_pk>",
        views.CreatePurchase.as_view(),
        name="create_purchase",
    ),
    path("manage_purchases", views.ManagePurchases.as_view(), name="manage_purchases"),
    path(
        "manage_user_purchases/<int:staff_pk>",
        views.ManageUserPurchases.as_view(),
        name="manage_user_purchases",
    ),
]
