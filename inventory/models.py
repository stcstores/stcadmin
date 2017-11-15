import os
import uuid

from django.db import models
from django.db.models import Q


def get_product_image_upload_to(instance, original_filename):
    extension = original_filename.split('.')[-1]
    filename = '{}.{}'.format(uuid.uuid4(), extension)
    return os.path.join('product_images', instance.range_id, filename)


class STCAdminImage(models.Model):
    range_id = models.CharField(max_length=10)
    image = models.ImageField(upload_to=get_product_image_upload_to)

    def delete(self, *args, **kwargs):
        image_path = self.image.path
        range_dir = os.path.dirname(image_path)
        if os.path.isfile(self.image.path):
            os.remove(self.image.path)
        if not os.listdir(range_dir):
            os.rmdir(range_dir)
        super(STCAdminImage, self).delete(*args, **kwargs)


class Barcode(models.Model):
    barcode = models.CharField(max_length=13, unique=True)
    used = models.BooleanField(default=False)

    def mark_used(self):
        self.used = True
        self.save()


def get_barcode():
    barcode = Barcode.objects.filter(used=False).all()[0]
    barcode.used = True
    barcode.save()
    return barcode.barcode


class DestinationCountry(models.Model):
    name = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.name


class PackageType(models.Model):
    name = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.name


class ShippingPriceManager(models.Manager):

    def get_price_for_product(self, country_name, product):
        package_type_name = str(product.options['Package Type'].value)
        country = DestinationCountry.objects.get(name__icontains=country_name)
        package_type = PackageType.objects.get(
            name__icontains=package_type_name)
        shipping_prices = self.get_queryset().filter(
            Q(country=country),
            Q(package_type=package_type),
            Q(min_wieght__isnull=True) | Q(min_wieght__lte=product.weight),
            Q(min_wieght__isnull=True) | Q(max_wieght__gte=product.weight))
        return self.get(pk=shipping_prices.all()[0].id)

    def calculate_price_for_product(self, country_name, product):
        return self.get_price_for_product.calculate()


class ShippingPrice(models.Model):
    country = models.ForeignKey(
        DestinationCountry, on_delete=models.CASCADE)
    package_type = models.ManyToManyField(PackageType)
    min_wieght = models.PositiveIntegerField(null=True, blank=True)
    max_wieght = models.PositiveIntegerField(null=True, blank=True)
    item_price = models.PositiveIntegerField()
    kilo_price = models.PositiveIntegerField(null=True, blank=True)

    objects = ShippingPriceManager()

    def __str__(self):
        package_types = '-'.join([str(x) for x in self.package_type.all()])
        weight = ''
        if self.min_wieght is not None:
            weight += '> {}'.format(self.min_wieght)
        if self.max_wieght is not None:
            weight += '< {}'.format(self.max_wieght)
        string = '{} {}'.format(self.country, package_types)
        if weight:
            string = '{} {}'.format(string, weight)
        return string

    def calculate(self, weight):
        return self.item_price + self.calculate_kilos(weight)

    def calculate_kilos(self, weight):
        if self.kilo_price is None:
            return 0
        return int((self.kilo_price / 1000) * weight)
