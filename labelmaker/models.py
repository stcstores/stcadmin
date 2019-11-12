"""Models for size charts."""

from collections import defaultdict

from django.db import models
from django.urls import reverse

from inventory.models import Supplier


class SizeChart(models.Model):
    """Model for size charts."""

    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=200)

    class Meta:
        """Meta class for SizeChart."""

        verbose_name = "Size Chart"
        verbose_name_plural = "Size Charts"
        ordering = ("name",)

    @classmethod
    def by_supplier(cls):
        """Return a dict of {SizeChart.supplier: SizeChart}."""
        size_charts = cls._default_manager.all().order_by("supplier__name", "name")
        supplier_dict = defaultdict(list)
        for chart in size_charts:
            supplier_dict[chart.supplier].append(chart)
        return dict(supplier_dict)

    def get_absolute_url(self):
        """Return URL for the object."""
        return reverse("labelmaker:size_chart_form", kwargs={"pk": str(self.id)})

    def get_delete_url(self):
        """Get URL to delete the object."""
        return reverse(
            "labelmaker:delete_size_chart", kwargs={"size_chart_id": str(self.id)}
        )

    def __str__(self):
        if self.supplier is not None:
            return f"{self.supplier.name} - {self.name}"
        else:
            return self.name


class SizeChartSize(models.Model):
    """Model for sizes used in size charts."""

    size_chart = models.ForeignKey("SizeChart", null=True, on_delete=models.CASCADE)
    sort = models.PositiveSmallIntegerField(default=0)
    name = models.CharField(max_length=300, null=True, blank=True, default=None)
    uk_size = models.CharField(max_length=200, verbose_name="UK Size")
    eu_size = models.CharField(max_length=200, verbose_name="EUR Size")
    us_size = models.CharField(max_length=200, verbose_name="USA Size")
    au_size = models.CharField(max_length=200, verbose_name="AUS Size")

    class Meta:
        """Meta class for SizeChartSize."""

        verbose_name = "Size Chart Size"
        verbose_name_plural = "Size Chart Sizes"
        ordering = ("sort",)

    def __str__(self):
        return "{} - UK {}".format(self.size_chart.name, self.uk_size)

    def get_sizes(self):
        """Return dict of sizes by country code."""
        return (
            ("UK", self.uk_size),
            ("EUR", self.eu_size),
            ("USA", self.us_size),
            ("AUS", self.au_size),
        )
