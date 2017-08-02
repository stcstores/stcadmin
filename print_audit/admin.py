from django.contrib import admin
from print_audit import models


@admin.register(models.CloudCommerceUser)
class CloudCommerceUserAdmin(admin.ModelAdmin):
    fields = ['full_name', 'user_id', ]
    list_display = ('user_id', 'full_name')
    readonly_fields = ('full_name', )

    def __str__(self):
        return str(self.user_id)


@admin.register(models.CloudCommerceOrder)
class CloudCommerceOrderAdmin(admin.ModelAdmin):
    list_display = (
        'order_id', 'user_id', 'date_created', 'date_completed', 'attempts',
        'customer_id')
    date_hierarchy = 'date_created'


@admin.register(models.Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    pass


@admin.register(models.UserFeedback)
class UserFeedbackAdmin(admin.ModelAdmin):
    list_display = ('user', 'feedback_type', 'timestamp')
