from django.conf.urls import include, url  # noqa
from django.contrib import admin  # noqa

from print_audit import views

app_name = 'print_audit'

urlpatterns = [
    url(r'^index$', views.index, name='index'),

    url(r'^user_feedback$', views.user_feedback, name='user_feedback'),

    url(
        r'^create_feedback$',
        views.CreateUserFeedback.as_view(), name='create_feedback'),

    url(
        r'^create_feedback/(?P<user_id>[0-9]+)/$',
        views.CreateUserFeedback.as_view(), name='create_feedback'),

    url(
        r'^update_feedback/(?P<feedback_id>[0-9]+)/$',
        views.UpdateUserFeedback.as_view(), name='update_feedback'),

    url(
        r'^delete_feedback/(?P<feedback_id>[0-9]+)/$',
        views.delete_user_feedback, name='delete_feedback'),

    url(
        r'^display_monitor$',
        views.display_monitor, name='display_monitor'),

    url(
        r'^pack_count_monitor$',
        views.pack_count_monitor, name='pack_count_monitor'),

    url(
        r'^feedback_monitor$',
        views.feedback_monitor, name='feedback_monitor'),

    url(
        r'^feedback_list$',
        views.FeedbackList.as_view(), name='feedback_list'),

    url(
        r'^charts$',
        views.charts, name='charts'),

    url(
        r'^get_chart$',
        views.get_chart, name='get_chart'),

]
