import os

from ccapi import CCAPI
from django.db import models
from tabler import Table
from stcadmin import settings


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


class LocationIntegrityCheck:
    header = [
        'Duplicates', 'Missing form DB', 'Missing from CC',
        'Incorrect Information']
    output_dir = os.path.join(settings.MEDIA_ROOT, 'logs')
    output_file = os.path.join(output_dir, 'bay_integrity.csv')

    def __init__(self):
        self.bays = self.get_bays()
        self.duplicate_bays()
        self.missing_bays()
        self.excess_bays()
        self.incorrect_bays()
        print('Duplicate Bays: {}'.format(len(self.duplicate_bays)))
        print('Bays missing from Database: {}'.format(
            len(self.missing_bays)))
        print('Bays missing from Cloud Commerce: {}'.format(
            len(self.excess_bays)))
        print('Bays with non matching information: {}'.format(
            len(self.incorrect_bays)))

    def get_bays(self):
        warehouses = [v for k, v in CCAPI.get_warehouses().items()]
        bays = []
        for warehouse in warehouses:
            for bay in warehouse.bays:
                bays.append(bay)
        return bays

    def duplicate_bays(self):
        bay_names = [b.name for b in self.bays]
        duplicate_bay_names = [n for n in bay_names if bay_names.count(n) > 1]
        self.duplicate_bays = [
            b for b in self.bays if b.name in duplicate_bay_names]

    def missing_bays(self):
        self.missing_bays = [
            b for b in self.bays if not
            Bay.objects.filter(bay_id=b.id).exists()]

    def excess_bays(self):
        bay_ids = [int(b.id) for b in self.bays]
        self.excess_bays = [
            b for b in Bay.objects.all() if b.bay_id not in bay_ids]

    def incorrect_bays(self):
        matched_bays = [b for b in self.bays if not any([
            b in self.duplicate_bays, b in self.missing_bays,
            b in self.excess_bays])]
        incorrect_bays = []
        for bay in matched_bays:
            db_bay = Bay.objects.get(bay_id=bay.id)
            bay_invalid = any([
                bay.name != db_bay.name, bay.warehouse.id != bay.warehouse.id])
            if bay_invalid:
                incorrect_bays.append(bay)
        self.incorrect_bays = incorrect_bays

    def format_bay(self, bay):
        if isinstance(bay, Bay):
            return str(bay)
        return '{} - {}'.format(bay.warehouse.name, bay.name)

    def create_output(self):
        bay_lists = [
            self.duplicate_bays, self.missing_bays, self.excess_bays,
            self.incorrect_bays]
        data = []
        for i in range(max([len(l) for l in bay_lists])):
            row = []
            for bay_list in bay_lists:
                try:
                    row.append(self.format_bay(bay_list[i]))
                except IndexError:
                    row.append('')
            data.append(row)
        output = Table(header=self.header, data=data)
        output.write(self.output_file)

    def auto_add_to_db(self):
        bays = []
        for bay in self.missing_bays:
            warehouse = Warehouse.objects.get(warehouse_id=bay.warehouse.id)
            bays.append(Bay(name=bay.name, bay_id=bay.id, warehouse=warehouse))
        Bay.objects.bulk_create(bays)

    def auto_delete_from_db(self):
        for bay in self.excess_bays:
            bay.delete()


def check_location_integrity():
    integrity_check = LocationIntegrityCheck()
    integrity_check.create_output()
    return integrity_check
