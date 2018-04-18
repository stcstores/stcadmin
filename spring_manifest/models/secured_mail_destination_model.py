from django.db import models


class SecuredMailDestination(models.Model):
    name = models.CharField(max_length=255)
    manifest_row_number = models.PositiveIntegerField()

    def __str__(self):
        return self.name
