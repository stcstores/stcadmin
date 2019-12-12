"""URLs for the Feedback app."""
from django.urls import path

from feedback import views

app_name = "feedback"

urlpatterns = [
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
        "delete_feedback/<int:pk>/",
        views.DeleteUserFeedback.as_view(),
        name="delete_feedback",
    ),
    path("feedback_list/", views.FeedbackList.as_view(), name="feedback_list"),
    path(
        "feedback_quickview/",
        views.FeedbackQuickview.as_view(),
        name="feedback_quickview",
    ),
    path(
        "feedback_details/<int:feedback_id>/",
        views.FeedbackDetails.as_view(),
        name="feedback_details",
    ),
]
