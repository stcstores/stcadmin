from django.conf.urls import include, url
from django.contrib import admin

from labelmaker import views

app_name = 'labelmaker'

urlpatterns = [
    url(
        r'^create_size_chart$', views.EditSizeChart.as_view(),
        name='create_size_chart'),
    url(
        r'^edit_size_chart/(?P<size_chart_id>[0-9]+)/$',
        views.EditSizeChart.as_view(), name='edit_size_chart'),
    url(
        r'^create_size_chart_form$', views.create_size_chart_form,
        name='create_size_chart_form'),
    url(r'^size_charts', views.size_charts, name='size_charts'),
    url(
        r'^edit_size_chart_form/(?P<size_chart_id>[0-9]+)/$',
        views.edit_size_chart_form, name='edit_size_chart_form'),
    url(
        r'^label_form/(?P<size_chart_id>[0-9]+)/$',
        views.label_form_size_chart, name='label_form'),
    url(
        r'^label_form/$', views.label_form_no_size_chart,
        name='label_form'),
    url(
        r'^generate_pdf_no_size_chart/',
        views.generate_pdf_no_size_chart, name='generate_pdf_no_size_chart'),
    url(
        r'^generate_pdf_for_size_chart/(?P<size_chart_id>[0-9]+)/$',
        views.generate_pdf_for_size_chart, name='generate_pdf_for_size_chart'),
    url(
        r'^delete_size_chart/(?P<size_chart_id>[0-9]+)/$',
        views.delete_size_chart, name='delete_size_chart'),
    url(r'^test$', views.test_pdf, name='test_pdf'),
    url(r'^$', views.index, name='index'),
]
