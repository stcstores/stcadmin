"""Models for managing packing mistakes."""

from django.db import models
from django.shortcuts import reverse
from django.utils import timezone

from home.models import Staff


class PackingMistakeManager(models.Manager):
    """
    Manager for the PackingMistake model.

    Limits query results to those dated with in the current month.
    """

    def get_queryset(self):
        """Return QuerySet of User Feedback dated in the current month."""
        current_time = timezone.now()
        return (
            super()
            .get_queryset()
            .filter(
                timestamp__month=current_time.month, timestamp__year=current_time.year
            )
        )


class PackingMistake(models.Model):
    """Model for recording packing mistakes."""

    user = models.ForeignKey(
        Staff, on_delete=models.CASCADE, related_name="packing_mistakes"
    )
    timestamp = models.DateField(default=timezone.now)
    order_id = models.CharField(max_length=10, blank=True, null=True)
    note = models.TextField(blank=True, null=True)

    objects = models.Manager()
    this_month = PackingMistakeManager()

    class Meta:
        """Meta class for PackingMistake."""

        verbose_name = "Packing Mistake"
        verbose_name_plural = "Packing Mistakes"
        ordering = ("-timestamp",)

    def __str__(self):
        return f"Packing Mistake for {self.user.full_name()}"

    def get_absolute_url(self):
        """Return the absolute URL for this object."""
        return reverse("orders:update_packing_mistake", kwargs={"pk": self.pk})
