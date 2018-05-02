"""Counter model."""

from django.db import models


class Counter(models.Model):
    """Model for counting values."""

    name = models.CharField(max_length=255)
    count = models.PositiveIntegerField()

    def __str__(self):
        return self.name
