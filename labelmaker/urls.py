"""URL patters for the labelmaker app."""

from django.urls import path
from labelmaker import views

app_name = "labelmaker"

urlpatterns = [
    path(
        "create_size_chart/",
        views.CreateSizeChart.as_view(),
        name="create_size_chart_form",
    ),
    path("size_charts/", views.SizeCharts.as_view(), name="size_charts"),
    path(
        "label_form/<int:size_chart_id>/",
        views.ProductLabelFormSizeChart.as_view(),
        name="label_form",
    ),
    path("label_form/", views.ProductLabelFormNoSizeChart.as_view(), name="label_form"),
    path(
        "generate_pdf_no_size_chart/",
        views.ProductLabelsPDFNoSizeChart.as_view(),
        name="generate_pdf_no_size_chart",
    ),
    path(
        "generate_pdf_for_size_chart/<int:size_chart_id>/",
        views.ProductLabelsPDFFromSizeChart.as_view(),
        name="generate_pdf_for_size_chart",
    ),
    path(
        "delete_size_chart/<int:size_chart_id>/",
        views.DeleteSizeChart.as_view(),
        name="delete_size_chart",
    ),
    path("test/", views.TestProductPDFLabel.as_view(), name="test_pdf"),
    path(
        "size_chart_form/<int:pk>/",
        views.SizeChartForm.as_view(),
        name="size_chart_form",
    ),
    path("product_labels/", views.ProductLabels.as_view(), name="product_labels"),
    path("", views.Index.as_view(), name="index"),
]
