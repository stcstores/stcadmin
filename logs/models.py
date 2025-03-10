"""Models for the logs app."""

from django.db import models
from django.utils import timezone

from home.models import Staff


class FBALogUsers(models.Model):
    """Model for users shown in FBA logs."""

    staff_member = models.OneToOneField(
        Staff, related_name="is_on_fba_log", on_delete=models.PROTECT
    )

    class Meta:
        """Meta class for WorkLog."""

        verbose_name = "Work Log User"
        verbose_name_plural = "Work Log Users"

    def __str__(self):
        return self.staff_member.full_name()


class WorkLog(models.Model):
    """Model for work logs."""

    created_at = models.DateTimeField(default=timezone.now)
    modified_at = models.DateTimeField(auto_now=True)

    staff_member = models.ForeignKey(
        Staff,
        on_delete=models.PROTECT,
        related_name="work_logs",
    )
    date = models.DateField()
    job = models.TextField()

    class Meta:
        """Meta class for WorkLog."""

        verbose_name = "Work Log"
        verbose_name_plural = "Work Logs"

    def __str__(self):
        return f"{self.staff_member} - {self.job} - {self.date}"
