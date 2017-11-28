from django.contrib import admin
from labelmaker import models


@admin.register(models.SizeChart)
class SizeChartAdmin(admin.ModelAdmin):
    fields = ('name', )


@admin.register(models.SizeChartSize)
class SizeChartSizeAdmin(admin.ModelAdmin):
    fields = (
        'size_chart', 'name', 'uk_size', 'eu_size', 'us_size', 'au_size',
        'sort')

    list_display = fields
