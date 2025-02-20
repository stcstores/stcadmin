"""URLs for the logs app."""

from django.urls import path

from logs import views

app_name = "logs"

urlpatterns = [
    path("", views.Index.as_view(), name="index"),
    path("fba_logs", views.FBALogDate.as_view(), name="fba_logs"),
    path(
        "fba_logs/<int:year>/<int:month>/<int:day>",
        views.FBALog.as_view(),
        name="fba_logs",
    ),
    path(
        "update_work_logs/<int:year>/<int:month>/<int:day>",
        views.UpdateWorkLog.as_view(),
        name="update_work_logs",
    ),
]
