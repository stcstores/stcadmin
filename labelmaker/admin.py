"""Model admin for labelmaker app."""

from django.contrib import admin
from labelmaker import models


@admin.register(models.SizeChart)
class SizeChartAdmin(admin.ModelAdmin):
    """Model admin for SizeChart model."""

    fields = ("name",)


@admin.register(models.SizeChartSize)
class SizeChartSizeAdmin(admin.ModelAdmin):
    """Model admin for SizeChartSize model."""

    fields = ("size_chart", "name", "uk_size", "eu_size", "us_size", "au_size", "sort")
    list_display = fields
