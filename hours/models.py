"""Models for the Hours app."""

from django.db import models
from django.utils import timezone

from home.models import Staff


class ClockTime(models.Model):
    """Model for storing clock ins and outs."""

    IN = "In"
    OUT = "Out"

    user = models.ForeignKey(
        Staff, on_delete=models.PROTECT, related_name="clock_hours"
    )
    timestamp = models.DateTimeField(default=timezone.now)

    class Meta:
        """Meta class for the ClockTime model."""

        verbose_name = "Clock Time"
        verbose_name_plural = "Clock Times"
        ordering = ("timestamp",)
        unique_together = [["user", "timestamp"]]
        get_latest_by = "timestamp"

    class ClockTimeManager(models.Manager):
        """Manager for the ClockTime model."""

        def clock(self, user):
            """Create a clock time."""
            now = timezone.now()
            try:
                latest = self.filter(user=user).latest().timestamp
            except self.model.DoesNotExist:
                pass
            else:
                if all(
                    (
                        latest.year == now.year,
                        latest.month == now.month,
                        latest.day == now.day,
                        latest.hour == now.hour,
                        latest.minute == now.minute,
                    ),
                ):
                    raise self.model.ClockedTooSoonError()
            obj = self.create(user=user, timestamp=now)
            return obj

    class ClockedTooSoonError(ValueError):
        """Error raised when two clocks are recorded for the same user in the same minute."""

        def __init__(self, *args, **kwargs):
            """Raise error."""
            super().__init__(self, "Clocked too soon.")

    objects = ClockTimeManager()

    def __str__(self):
        return f"Clock {self.user} at {self.timestamp}"

    def direction(self):
        """Return ClockTime.IN or ClockTime.OUT."""
        earlier_times = ClockTime.objects.filter(
            user=self.user, timestamp__range=(self.timestamp.date().min, self.timestamp)
        ).exclude(id=self.id)
        if earlier_times.count() % 2 == 0:
            return self.IN
        return self.OUT
