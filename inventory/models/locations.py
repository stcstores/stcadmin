"""Models for storing Warehouse Bay Locations."""


from django.db import models


class Bay(models.Model):
    """Model for Warehouse Bays."""

    name = models.CharField(max_length=255, unique=True)
    active = models.BooleanField(default=True)

    objects = models.Manager()

    class Meta:
        """Meta class for Bay."""

        verbose_name = "Bay"
        verbose_name_plural = "Bays"
        ordering = ("name",)

    def __str__(self):
        return self.name

    @staticmethod
    def backup_bay_name(*, bay_name, backup_location):
        """Return the name for a backup bay."""
        return f"Backup {backup_location.name} {bay_name}"

    @classmethod
    def new_backup_bay(cls, name, backup_location):
        """Return a new Bay instance named as a backup bay."""
        backup_name = cls.backup_bay_name(
            bay_name=name, backup_location=backup_location
        )
        return cls(name=backup_name)

    @property
    def is_backup(self):
        """Return True if the bay is a backup bay, otherwise False."""
        return "Backup" in self.name

    @property
    def is_primary(self):
        """Return True if the bay is a primary bay, otherwise False."""
        if not self.is_backup and not self.is_default:
            return True
        return False
