"""URLs for the purchases app."""

from django.urls import path

from purchases import views

app_name = "purchases"
urlpatterns = [
    path("", views.Index.as_view(), name="index"),
    path("product_search", views.ProductSearch.as_view(), name="product_search"),
    path(
        "create_product_purchase/<int:product_pk>",
        views.CreateProductPurchase.as_view(),
        name="create_product_purchase",
    ),
    path(
        "create_shipping_purchase",
        views.CreateShippingPurchase.as_view(),
        name="create_shipping_purchase",
    ),
    path(
        "create_other_purchase",
        views.CreateOtherPurchase.as_view(),
        name="create_other_purchase",
    ),
    path(
        "update_product_purchase/<int:pk>",
        views.UpdateProductPurchase.as_view(),
        name="update_product_purchase",
    ),
    path(
        "update_shipping_purchase/<int:pk>",
        views.UpdateShippingPurchase.as_view(),
        name="update_shipping_purchase",
    ),
    path(
        "update_other_purchase/<int:pk>",
        views.UpdateOtherPurchase.as_view(),
        name="update_other_purchase",
    ),
    path("manage_purchases", views.ManagePurchases.as_view(), name="manage_purchases"),
    path(
        "manage_user_purchases/<int:staff_pk>",
        views.ManageUserPurchases.as_view(),
        name="manage_user_purchases",
    ),
    path(
        "delete_purchase/<int:pk>",
        views.DeletePurchase.as_view(),
        name="delete_purchase",
    ),
    path("purchase_reports", views.PurchaseReports.as_view(), name="purchase_reports"),
    path(
        "download_purchase_report/<int:pk>",
        views.DownloadPurchaseReport.as_view(),
        name="download_purchase_report",
    ),
]
