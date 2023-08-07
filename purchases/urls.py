"""URLs for the purchases app."""

from django.urls import path

from purchases import views

app_name = "purchases"
urlpatterns = [
    path("", views.ProductSearch.as_view(), name="product_search"),
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
    path(
        "update_purchase/<int:pk>",
        views.UpdatePurchase.as_view(),
        name="update_purchase",
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
