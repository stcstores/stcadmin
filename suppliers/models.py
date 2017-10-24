from django.db import models
from django.contrib import admin


class Supplier(models.Model):
    name = models.CharField(max_length=200, unique=True)
    email = models.CharField(max_length=200, null=True, blank=True)
    phone = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        return self.name


class SupplierAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone')


class StockItem(models.Model):
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)
    product_code = models.CharField(max_length=200, unique=True)
    supplier_title = models.CharField(max_length=200)
    box_quantity = models.PositiveSmallIntegerField(blank=True, null=True)
    linnworks_title = models.CharField(max_length=200, null=True, blank=True)
    linnworks_sku = models.CharField(max_length=200, null=True, blank=True)
    notes = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        return self.linnworks_title


class StockItemAdmin(admin.ModelAdmin):
    list_display = (
        'product_code', 'supplier_title', 'box_quantity', 'linnworks_title',
        'linnworks_sku', 'supplier',)


admin.site.register(Supplier, SupplierAdmin)
admin.site.register(StockItem, StockItemAdmin)
