"""Models for Stock Check app."""

from django.db import models


class DuplicateBayManager(models.Manager):
    """Model manager for finding bays with duplicate names."""

    def get_queryset(self, *args, **kwargs):
        """Return queryset of bays with duplicate names."""
        queryset = super().get_queryset(*args, **kwargs)
        dupes = queryset.values('name').annotate(
            models.Count('id')).filter(id__count__gt=1)
        return queryset.filter(name__in=[item['name'] for item in dupes])


class Warehouse(models.Model):
    """The Warehouse model stores Cloud Commerce Warehouses."""

    class Meta:
        """Sort by name."""

        ordering = ('name', )

    warehouse_id = models.PositiveIntegerField(
        verbose_name='Warehouse ID', primary_key=False, unique=True,
        db_index=True)
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Bay(models.Model):
    """The Bay model stores Cloud Commerce Warehouse Bays."""

    class Meta:
        """Stort by name."""

        ordering = ('name', )

    bay_id = models.PositiveIntegerField(
        verbose_name='Bay ID', primary_key=False, unique=True, db_index=True)
    name = models.CharField(max_length=50, unique=True)
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE)

    objects = models.Manager()
    duplicates = DuplicateBayManager()

    def __str__(self):
        return '{}: {}'.format(self.warehouse, self.name)


class Product(models.Model):
    """The Product models stores Cloud Commerce Products."""

    range_id = models.PositiveIntegerField(
        verbose_name='Range ID', primary_key=False, null=True, blank=True)
    product_id = models.PositiveIntegerField(
        verbose_name='Product ID', primary_key=False, unique=True,
        db_index=True, null=True, blank=True)
    sku = models.CharField(max_length=50, db_index=True, unique=True)
    bays = models.ManyToManyField(Bay, through='ProductBay')

    def bay_names(self):
        """Return list of bay names as a string."""
        return ', '.join([str(bay) for bay in self.bays.all()])

    def __str__(self):
        return self.sku


class ProductBay(models.Model):
    """THe ProductBay model stores the quantity of a product in a Bay."""

    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    bay = models.ForeignKey(Bay, on_delete=models.CASCADE)
    stock_level = models.PositiveIntegerField(
        blank=True, null=True, default=None)
