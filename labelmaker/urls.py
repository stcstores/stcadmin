from django.urls import path
from labelmaker import views

app_name = 'labelmaker'

urlpatterns = [
    path(
        'create_size_chart/', views.CreateSizeChart.as_view(),
        name='create_size_chart_form'),
    path('size_charts/', views.SizeCharts.as_view(), name='size_charts'),
    path(
        'label_form/<int:size_chart_id>/',
        views.LabelFormSizeChart.as_view(), name='label_form'),
    path(
        'label_form/', views.LabelFormNoSizeChart.as_view(),
        name='label_form'),
    path(
        'generate_pdf_no_size_chart/',
        views.LabelPDF.as_view(), name='generate_pdf_no_size_chart'),
    path(
        'generate_pdf_for_size_chart/<int:size_chart_id>/',
        views.LabelPDF.as_view(), name='generate_pdf_for_size_chart'),
    path(
        'delete_size_chart/<int:size_chart_id>/',
        views.DeleteSizeChart.as_view(), name='delete_size_chart'),
    path('test/', views.TestPDFLabel.as_view(), name='test_pdf'),
    path(
        'size_chart_form/<int:pk>/',
        views.SizeChartForm.as_view(), name='size_chart_form'),
    path('', views.Index.as_view(), name='index'),
]
