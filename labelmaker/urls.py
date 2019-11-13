"""URL patters for the labelmaker app."""

from django.urls import path

from labelmaker import views

app_name = "labelmaker"

urlpatterns = [
    path("", views.Index.as_view(), name="index"),
    path("product_labels/", views.ProductLabels.as_view(), name="product_labels"),
    path(
        "product_labels/create_size_chart/",
        views.CreateSizeChart.as_view(),
        name="create_size_chart",
    ),
    path(
        "product_labels/edit_size_chart_sizes/<int:id>/",
        views.EditSizeChartSizes.as_view(),
        name="edit_size_chart_sizes",
    ),
    path(
        "product_labels/update_size_chart/<int:pk>/",
        views.UpdateSizeChart.as_view(),
        name="update_size_chart",
    ),
    path(
        "product_labels/delete_size_chart/<int:id>/",
        views.DeleteSizeChart.as_view(),
        name="delete_size_chart",
    ),
    path(
        "product_labels/create_product_labels/<int:id>/",
        views.CreateProductLabelsWithTemplate.as_view(),
        name="create_product_labels",
    ),
    path(
        "product_labels/create_product_labels/",
        views.CreateProductLabelsWithoutTemplate.as_view(),
        name="create_product_labels",
    ),
    path(
        "product_labels/generate_pdf_no_size_chart/",
        views.ProductLabelsPDFNoSizeChart.as_view(),
        name="generate_pdf_no_size_chart",
    ),
    path(
        "product_labels/generate_pdf_for_size_chart/<int:id>/",
        views.ProductLabelsPDFFromSizeChart.as_view(),
        name="generate_pdf_for_size_chart",
    ),
    path("product_labels/test/", views.TestProductPDFLabel.as_view(), name="test_pdf"),
    path("address_labels/", views.AddressLabelForm.as_view(), name="address_labels"),
    path(
        "address_labels/address_label_pdf",
        views.AddressLabelPDF.as_view(),
        name="address_label_pdf",
    ),
    path("small_labels/", views.SmallLabelForm.as_view(), name="small_labels"),
    path(
        "small_labels/small_label_pdf/",
        views.SmallLabelPDF.as_view(),
        name="small_label_pdf",
    ),
]
