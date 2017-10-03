from django.db import models


class DestinationZone(models.Model):
    name = models.CharField(max_length=50)
    code = models.CharField(max_length=3)

    class Meta:
        ordering = ('name', )

    def safe_name(self):
        return self.name.lower().replace(' ', '_')

    def __str__(self):
        return str(self.name)


class CloudCommerceCountryID(models.Model):

    name = models.CharField(max_length=50)
    cc_id = models.IntegerField()
    iso_code = models.CharField(
        max_length=3, blank=True, null=True, verbose_name='ISO Code')
    zone = models.ForeignKey(DestinationZone, blank=True, null=True)

    class Meta:
        ordering = ('name', )

    def __str__(self):
        return str(self.name)
