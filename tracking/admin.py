"""Model admin for the tracking app."""

from django.contrib import admin

from tracking import models


@admin.register(models.TrackingCarrier)
class TrackingCarrierAdmin(admin.ModelAdmin):
    """Admin for the tracking.TrackingCarrierAdmin model."""

    fields = ("name", "slug", "tracking_number_match")
    list_display = ("name", "slug", "tracking_number_match")
    list_editable = ("tracking_number_match",)
    search_fields = ("name", "slug", "tracking_number_match")


@admin.register(models.TrackedPackage)
class TrackedPackageAdmin(admin.ModelAdmin):
    """Admin for the tracking.TrackedPackage model."""

    fields = (
        "scurri_id",
        "carrier",
        "tracking_number",
        "created_at",
        "carrier_contacted",
        "notes",
    )
    list_display = (
        "scurri_id",
        "carrier",
        "tracking_number",
        "created_at",
        "carrier_contacted",
        "notes",
    )
    list_editable = ("carrier_contacted", "notes")
    search_fields = ("scurri_id", "tracking_number")
    date_hierarchy = "created_at"
    list_filter = ("carrier",)


@admin.register(models.TrackingEvent)
class TrackingEventAdmin(admin.ModelAdmin):
    """Admin for the tracking.TrackingEvent model."""

    fields = (
        "event_id",
        "package",
        "status",
        "carrier_code",
        "description",
        "timestamp",
        "location",
    )
    list_display = (
        "event_id",
        "package",
        "status",
        "carrier_code",
        "description",
        "timestamp",
        "location",
    )
    search_fields = ("event_id", "package__scurri_id")
    date_hierarchy = "timestamp"
    list_filter = ("package__carrier",)
