from django.db import models
from django.contrib import admin
from django.urls import reverse


class SizeChart(models.Model):
    class Meta:
        ordering = ('name',)

    name = models.CharField(max_length=200)

    def get_absolute_url(self):
        return reverse(
            'labelmaker:edit_size_chart_form', args=[str(self.id)])

    def __str__(self):
        return self.name


class SizeChartSize(models.Model):
    class Meta:
        ordering = ('sort',)

    supplier = models.ForeignKey('SizeChart', on_delete=models.CASCADE)
    sort = models.PositiveSmallIntegerField(default=0)
    name = models.CharField(
        max_length=300, null=True, blank=True, default=None)
    uk_size = models.CharField(max_length=200, verbose_name='UK Size')
    eu_size = models.CharField(max_length=200, verbose_name='EUR Size')
    us_size = models.CharField(max_length=200, verbose_name='USA Size')
    au_size = models.CharField(max_length=200, verbose_name='AUS Size')

    def __str__(self):
        return self.supplier.name + ' - UK ' + self.uk_size

    def get_absolute_url(self):
        return reverse(
            'labelmaker.views.edit_size_chart_form',
            args=[str(self.supplier.id)])

    def get_sizes(self):
        return [
            ['UK', self.uk_size], ['EUR', self.eu_size], ['USA', self.us_size],
            ['AUS', self.au_size]]


class SizeChartAdmin(admin.ModelAdmin):
    fields = ['name']


class SizeChartSizeAdmin(admin.ModelAdmin):
    fields = [
        'supplier', 'name', 'uk_size', 'eu_size', 'us_size', 'au_size',
        'sort']
    list_display = fields

admin.site.register(SizeChart, SizeChartAdmin)
admin.site.register(SizeChartSize, SizeChartSizeAdmin)
