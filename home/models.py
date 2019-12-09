"""Models for the Home app."""

from django.contrib.auth.models import User
from django.db import models


class UnHidden(models.Manager):
    """Manager for Cloud Commerce Users that are not hidden."""

    def get_queryset(self, *args, **kwargs):
        """Return queryset of Cloud Commerce Users that are not hidden."""
        queryset = super().get_queryset(*args, **kwargs)
        return queryset.filter(hidden=False)


class CloudCommerceUser(models.Model):
    """Model for storing details of Cloud Commerce Users."""

    user_id = models.CharField(max_length=10, unique=True)
    stcadmin_user = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="_stcadmin_user",
    )
    first_name = models.CharField(max_length=50)
    second_name = models.CharField(max_length=50)
    hidden = models.BooleanField(default=False)

    objects = models.Manager()
    unhidden = UnHidden()

    class Meta:
        """Meta class for CloudCommerceUser."""

        verbose_name = "Cloud Commerce User"
        verbose_name_plural = "Cloud Commerce Users"

    def __repr__(self):
        return self.full_name()

    def __str__(self):
        return self.full_name()

    def full_name(self):
        """Return user's full name."""
        return "{} {}".format(self.first_name, self.second_name)
