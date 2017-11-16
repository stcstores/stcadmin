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

    def get_price_for_product(self, country_name, price, product):
        package_type_name = str(product.options['Package Type'].value)
        weight = product.weight
        return self.get_price(country_name, package_type_name, weight)

    def get_price(self, country_name, package_type_name, weight, price):
        country = DestinationCountry.objects.get(name__icontains=country_name)
        package_type = PackageType.objects.get(
            name__icontains=package_type_name)
        shipping_prices = self.get_queryset().filter(Q(country=country))
        shipping_prices = shipping_prices.filter(Q(package_type=package_type))
        shipping_prices = shipping_prices.filter(
            Q(min_weight__isnull=True) | Q(min_weight__lte=weight))
        shipping_prices = shipping_prices.filter(
            Q(max_weight__isnull=True) | Q(max_weight__gte=weight))
        shipping_prices = shipping_prices.filter(
            Q(min_price__isnull=True) | Q(min_price__lte=price))
        shipping_prices = shipping_prices.filter(
            Q(max_price__isnull=True) | Q(max_price__gte=price))
        print(shipping_prices.all())
        return self.get(pk=shipping_prices.all()[0].id)

    def get_calculated_price(
            self, country_name, package_type_name, weight, price):
        return self.get_price(
            country_name, package_type_name, weight, price).calculate(weight)

    def calculate_price_for_product(self, country_name, price, product):
        return self.get_price_for_product(
            country_name, price, product).calculate()


class ShippingPrice(models.Model):
    name = models.CharField(max_length=50, unique=True)
    country = models.ForeignKey(
        DestinationCountry, on_delete=models.CASCADE)
    package_type = models.ManyToManyField(PackageType)
    min_weight = models.PositiveIntegerField(null=True, blank=True)
    max_weight = models.PositiveIntegerField(null=True, blank=True)
    min_price = models.PositiveIntegerField(null=True, blank=True)
    max_price = models.PositiveIntegerField(null=True, blank=True)
    item_price = models.PositiveIntegerField()
    kilo_price = models.PositiveIntegerField(null=True, blank=True)

    objects = ShippingPriceManager()

    def __str__(self):
        return self.name

    def calculate(self, weight):
        return self.item_price + self.calculate_kilos(weight)

    def calculate_kilos(self, weight):
        if self.kilo_price is None:
            return 0
        return int((self.kilo_price / 1000) * weight)

    def package_type_string(self):
        return ', '.join([x.name for x in self.package_type.all()])
