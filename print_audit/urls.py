"""URLs for print audit app."""

from django.urls import path

from print_audit import views

app_name = "print_audit"

urlpatterns = [
    path("", views.Index.as_view(), name="index"),
    path("user_feedback/", views.UserFeedback.as_view(), name="user_feedback"),
    path(
        "create_feedback/", views.CreateUserFeedback.as_view(), name="create_feedback"
    ),
    path(
        "create_feedback/<int:user_id>/",
        views.CreateUserFeedback.as_view(),
        name="create_feedback",
    ),
    path(
        "update_feedback/<int:feedback_id>/",
        views.UpdateUserFeedback.as_view(),
        name="update_feedback",
    ),
    path(
        "delete_feedback/(<int:pk>/",
        views.DeleteUserFeedback.as_view(),
        name="delete_feedback",
    ),
    path("display_monitor/", views.DisplayMonitor.as_view(), name="display_monitor"),
    path(
        "pack_count_monitor/",
        views.PackCountMonitor.as_view(),
        name="pack_count_monitor",
    ),
    path("feedback_monitor/", views.FeedbackMonitor.as_view(), name="feedback_monitor"),
    path("feedback_list/", views.FeedbackList.as_view(), name="feedback_list"),
    path("charts/", views.Charts.as_view(), name="charts"),
    path(
        "feedback_quickview/",
        views.FeedbackQuickview.as_view(),
        name="feedback_quickview",
    ),
    path("breakages/", views.BreakageIndex.as_view(), name="breakages"),
    path("add_breakage/", views.AddBreakage.as_view(), name="add_breakage"),
    path(
        "update_breakage/<int:breakage_id>/",
        views.UpdateBreakage.as_view(),
        name="update_breakage",
    ),
    path(
        "delete_breakage/<int:breakage_id>/",
        views.DeleteBreakage.as_view(),
        name="delete_breakage",
    ),
    path(
        "feedback_details/<int:feedback_id>/",
        views.FeedbackDetails.as_view(),
        name="feedback_details",
    ),
]
