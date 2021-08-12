"""The Channel model."""
from django.db import models


class Channel(models.Model):
    """Model for sales channels."""

    name = models.CharField(max_length=255, unique=True, db_index=True)
    channel_fee = models.FloatField(default=15.5)

    class Meta:
        """Meta class for the Channel model."""

        verbose_name = "Channel"
        verbose_name_plural = "Channels"

    def __str__(self):
        return self.name
