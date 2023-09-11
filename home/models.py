"""Models for the Home app."""

from django.contrib.auth.models import User
from django.db import models


class UnHidden(models.Manager):
    """Manager for staff members that are not hidden."""

    def get_queryset(self, *args, **kwargs):
        """Return queryset of Staff objects that are not hidden."""
        queryset = super().get_queryset(*args, **kwargs)
        return queryset.filter(hidden=False)


class Staff(models.Model):
    """Model for storing details of staff members."""

    stcadmin_user = models.OneToOneField(
        User,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="staff_member",
    )
    first_name = models.CharField(max_length=50)
    second_name = models.CharField(max_length=50)
    email_address = models.EmailField(blank=True, null=True)
    fba_packer = models.BooleanField(default=False)
    hidden = models.BooleanField(default=False)

    objects = models.Manager()
    unhidden = UnHidden()

    class Meta:
        """Meta class for Staff."""

        verbose_name = "Staff"
        verbose_name_plural = "Staff"

    def __str__(self):
        return self.full_name()

    def full_name(self):
        """Return user's full name."""
        return "{} {}".format(self.first_name, self.second_name)


class ExternalLink(models.Model):
    """Model for external links."""

    name = models.CharField(max_length=255)
    url = models.URLField()
    ordering = models.PositiveSmallIntegerField(default=100)

    class Meta:
        """Meta class for the ExternalLink model."""

        verbose_name = "External Link"
        verbose_name_plural = "External Links"
        ordering = ("ordering",)
