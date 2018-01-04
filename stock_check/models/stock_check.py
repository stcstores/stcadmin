from django.db import models


class DuplicateBayManager(models.Manager):

    def get_queryset(self, *args, **kwargs):
        queryset = super().get_queryset(*args, **kwargs)
        dupes = queryset.values('name').annotate(
            models.Count('id')).filter(id__count__gt=1)
        return queryset.filter(name__in=[item['name'] for item in dupes])


class Warehouse(models.Model):

    class Meta:
        ordering = ('name', )

    warehouse_id = models.PositiveIntegerField(
        verbose_name='Warehouse ID', primary_key=False, unique=True,
        db_index=True)
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Bay(models.Model):

    class Meta:
        ordering = ('name', )

    bay_id = models.PositiveIntegerField(
        verbose_name='Bay ID', primary_key=False, unique=True, db_index=True)
    name = models.CharField(max_length=50)
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE)

    objects = models.Manager()
    duplicates = DuplicateBayManager()

    def __str__(self):
        return '{}: {}'.format(self.warehouse, self.name)


class Product(models.Model):

    range_id = models.PositiveIntegerField(
        verbose_name='Range ID', primary_key=False, null=True, blank=True)
    product_id = models.PositiveIntegerField(
        verbose_name='Product ID', primary_key=False, unique=True,
        db_index=True, null=True, blank=True)
    sku = models.CharField(max_length=50, db_index=True, unique=True)
    bays = models.ManyToManyField(Bay)

    def bay_names(self):
        return ', '.join([str(bay) for bay in self.bays.all()])

    def __str__(self):
        return self.sku
