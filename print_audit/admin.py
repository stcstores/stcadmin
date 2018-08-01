"""Model admin for print_audit."""

from django.contrib import admin

from print_audit import models


@admin.register(models.CloudCommerceUser)
class CloudCommerceUserAdmin(admin.ModelAdmin):
    """Model admin for CloudCommerceUser model."""

    fields = ["full_name", "user_id", "stcadmin_user", "hidden"]
    list_display = ("full_name", "user_id", "hidden")
    list_display_links = ("full_name",)
    list_editable = ("user_id", "hidden")
    readonly_fields = ("full_name",)

    def __str__(self):
        return str(self.user_id)


@admin.register(models.CloudCommerceOrder)
class CloudCommerceOrderAdmin(admin.ModelAdmin):
    """Model admin for CloudCommerceOrder model."""

    list_display = (
        "order_id",
        "user",
        "date_created",
        "date_completed",
        "attempts",
        "customer_id",
    )
    date_hierarchy = "date_created"
    list_filter = ("user", "date_created")
    list_editable = ("user",)


@admin.register(models.Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    """Model admin for Feedback model."""

    pass


@admin.register(models.UserFeedback)
class UserFeedbackAdmin(admin.ModelAdmin):
    """Model admin for UserFeedback model."""

    list_display = ("user", "feedback_type", "timestamp")


@admin.register(models.Breakage)
class BreakageAdmin(admin.ModelAdmin):
    """Model admin for Breackage model."""

    fields = ("product_sku", "order_id", "packer")
    list_display = ("__str__", "product_sku", "order_id", "note", "packer", "timestamp")
    list_display_links = ("__str__",)
    list_editable = ("product_sku", "order_id", "packer")
    date_hierarchy = "timestamp"
    search_fields = ("order_id", "product_sku")
    list_filter = ("packer",)
