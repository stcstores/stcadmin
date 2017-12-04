from django.conf.urls import url
from labelmaker import views

app_name = 'labelmaker'

urlpatterns = [
    url(
        r'^create_size_chart$', views.CreateSizeChart.as_view(),
        name='create_size_chart_form'),
    url(r'^size_charts', views.SizeCharts.as_view(), name='size_charts'),
    url(
        r'^label_form/(?P<size_chart_id>[0-9]+)/$',
        views.LabelFormSizeChart.as_view(), name='label_form'),
    url(
        r'^label_form/$', views.LabelFormNoSizeChart.as_view(),
        name='label_form'),
    url(
        r'^generate_pdf_no_size_chart/',
        views.LabelPDF.as_view(), name='generate_pdf_no_size_chart'),
    url(
        r'^generate_pdf_for_size_chart/(?P<size_chart_id>[0-9]+)/$',
        views.LabelPDF.as_view(), name='generate_pdf_for_size_chart'),
    url(
        r'^delete_size_chart/(?P<size_chart_id>[0-9]+)/$',
        views.DeleteSizeChart.as_view(), name='delete_size_chart'),
    url(r'^test$', views.TestPDFLabel.as_view(), name='test_pdf'),
    url(
        r'^size_chart_form/(?P<pk>[0-9]+)/$',
        views.SizeChartForm.as_view(), name='size_chart_form'),
    url(r'^$', views.Index.as_view(), name='index'),
]
