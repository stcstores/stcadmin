from django.db import models


class DestinationZone(models.Model):
    name = models.CharField(max_length=50)
    code = models.CharField(max_length=3)
    format_code = models.CharField(
        max_length=1, blank=True, null=True, default=None)

    class Meta:
        ordering = ('name', )

    def safe_name(self):
        return self.name.lower().replace(' ', '_')

    def __str__(self):
        return str(self.name)
