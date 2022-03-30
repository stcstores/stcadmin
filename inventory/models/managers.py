"""Managers for the inventory app."""

from django.db import models


class ActiveInactiveQueryset(models.QuerySet):
    """Filter objects based on the `active` attribute."""

    def active(self):
        """Return objects for which the `active` attribue is True."""
        return self.filter(active=True)

    def inactive(self):
        """Return objects for which the `active` attribue is False."""
        return self.filter(active=False)


class ActiveInactiveManager(models.Manager):
    """Manager for filtering active and inactive objects."""

    queryset_class = ActiveInactiveQueryset
    use_for_related_fields = True
