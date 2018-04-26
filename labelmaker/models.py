"""Models for size charts."""

from django.db import models
from django.urls import reverse


class SizeChart(models.Model):
    """Model for size charts."""

    class Meta:
        """Set default ordering."""

        ordering = ('name', )

    name = models.CharField(max_length=200)

    def get_absolute_url(self):
        """Return URL for the object."""
        return reverse(
            'labelmaker:size_chart_form', kwargs={'pk': str(self.id)})

    def get_delete_url(self):
        """Get URL to delete the object."""
        return reverse(
            'labelmaker:delete_size_chart',
            kwargs={'size_chart_id': str(self.id)})

    def __str__(self):
        return self.name


class SizeChartSize(models.Model):
    """Model for sizes used in size charts."""

    class Meta:
        """Set default ordering."""

        ordering = ('sort', )

    size_chart = models.ForeignKey('SizeChart', on_delete=models.CASCADE)
    sort = models.PositiveSmallIntegerField(default=0)
    name = models.CharField(
        max_length=300, null=True, blank=True, default=None)
    uk_size = models.CharField(max_length=200, verbose_name='UK Size')
    eu_size = models.CharField(max_length=200, verbose_name='EUR Size')
    us_size = models.CharField(max_length=200, verbose_name='USA Size')
    au_size = models.CharField(max_length=200, verbose_name='AUS Size')

    def __str__(self):
        return '{} - UK {}'.format(self.size_chart.name, self.uk_size)

    def get_sizes(self):
        """Return dict of sizes by country code."""
        return (
            ('UK', self.uk_size), ('EUR', self.eu_size), ('USA', self.us_size),
            ('AUS', self.au_size))
