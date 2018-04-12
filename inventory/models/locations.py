from django.db import models


class UsedWarehouseManager(models.Manager):

    def get_queryset(self):
        return super().get_queryset().exclude(warehouse_id=5610)


class Warehouse(models.Model):
    warehouse_id = models.PositiveIntegerField(primary_key=True)
    name = models.CharField(max_length=255, unique=True)
    abriviation = models.CharField(max_length=4, null=True, blank=True)

    objects = models.Manager()
    used_warehouses = UsedWarehouseManager()

    def __str__(self):
        return self.name

    @property
    def id(self):
        return self.warehouse_id

    @property
    def bays(self):
        return self.bay_set.exclude(name=self.name)

    @property
    def default_bay(self):
        return self.bay_set.get(name=self.name)


class NonDefaultBaysManager(models.Manager):

    def get_queryset(self):
        warehouse_names = [w.name for w in Warehouse._base_manager.all()]
        return super().get_queryset().exclude(name__in=warehouse_names)


class Bay(models.Model):
    bay_id = models.PositiveIntegerField(primary_key=True)
    name = models.CharField(max_length=255, unique=True)
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE)

    objects = models.Manager()
    non_default = NonDefaultBaysManager()

    def __str__(self):
        return '{} - {}'.format(self.warehouse, self.name)

    @property
    def id(self):
        return self.bay_id

    @property
    def default(self):
        return self.name == self.warehouse.name
