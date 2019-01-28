"""Models for storing Warehouse Bay Locations."""

import os
import sys

from ccapi import CCAPI
from django.conf import settings
from django.db import models
from tabler import Table


class UsedWarehouseManager(models.Manager):
    """Manager to filter out unused warehouses."""

    def get_queryset(self):
        """Return queryset containing used warehouses."""
        return super().get_queryset().exclude(warehouse_id=5610)


class Warehouse(models.Model):
    """Model for Warehouses."""

    warehouse_id = models.PositiveIntegerField(primary_key=True)
    name = models.CharField(max_length=255, unique=True)
    abriviation = models.CharField(max_length=4, null=True, blank=True)

    objects = models.Manager()
    used_warehouses = UsedWarehouseManager()

    class Meta:
        """Meta class for Warehouse."""

        verbose_name = "Warehouse"
        verbose_name_plural = "Warehouses"
        ordering = ("name",)

    def __str__(self):
        return self.name

    @property
    def id(self):
        """
        Return warehouse_id attribute.

        Prevents errors when the primary key is accessed by the usual id
        attribute.
        """
        return self.warehouse_id

    @property
    def bays(self):
        """Return all bays in this warehouse except the default bay."""
        return self.bay_set.exclude(name=self.name)

    @property
    def default_bay(self):
        """Return the default bay for this warehouse."""
        return self.bay_set.get(name=self.name)


class NonDefaultBaysManager(models.Manager):
    """Manager for non default Bays."""

    def get_queryset(self):
        """Return queryset of all non default Bays."""
        warehouse_names = [w.name for w in Warehouse._base_manager.all()]
        return super().get_queryset().exclude(name__in=warehouse_names)


class Bay(models.Model):
    """Model for Warehouse Bays."""

    bay_id = models.PositiveIntegerField(primary_key=True)
    name = models.CharField(max_length=255, unique=True)
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE)

    objects = models.Manager()
    non_default = NonDefaultBaysManager()

    class Meta:
        """Meta class for Bay."""

        verbose_name = "Bay"
        verbose_name_plural = "Bays"

    def __str__(self):
        return "{} - {}".format(self.warehouse, self.name)

    @property
    def id(self):
        """
        Return bay_id attribute.

        Prevents errors when the primary key is accessed by the usual id
        attribute.
        """
        return self.bay_id

    @property
    def default(self):
        """Return True if the bay is the default bay for it's warehouse."""
        return self.name == self.warehouse.name

    @staticmethod
    def backup_bay_name(*, bay_name, department, backup_location):
        """Return the name for a backup bay."""
        return f"{department.abriviation} Backup {backup_location.name} {bay_name}"


class LocationIntegrityCheck:
    """
    Check location integrity.

    Find discrepencies between STCAdmin bay database and Cloud Commerce bays.
    Save results as .csv in media/logs.
    """

    header = [
        "Duplicates",
        "Missing form DB",
        "Missing from CC",
        "Incorrect Information",
    ]
    output_dir = os.path.join(settings.MEDIA_ROOT, "logs")
    output_file = os.path.join(output_dir, "bay_integrity.csv")

    def __init__(self):
        """
        Find discrepencies between Cloud Commerce and STCAdmin database.

        Save discrepencies to .csv and print to stdout.
        """
        self.bays = self.get_bays()
        self.duplicate_bays()
        self.missing_bays()
        self.excess_bays()
        self.incorrect_bays()
        print(f"Duplicate Bays: {len(self.duplicate_bays)}", file=sys.stderr)
        print(f"Bays missing from Database: {len(self.missing_bays)}", file=sys.stderr)
        print(
            f"Bays missing from Cloud Commerce: {len(self.excess_bays)}",
            file=sys.stderr,
        )
        print(
            f"Bays with non matching information: {len(self.incorrect_bays)}",
            file=sys.stderr,
        )

    def get_bays(self):
        """Return list of bays present in Cloud Commerce."""
        warehouses = [v for k, v in CCAPI.get_warehouses().items()]
        bays = []
        for warehouse in warehouses:
            for bay in warehouse.bays:
                bays.append(bay)
        return bays

    def duplicate_bays(self):
        """Create list of bays with duplicate names in Cloud Commerce."""
        bay_names = [b.name for b in self.bays]
        duplicate_bay_names = [n for n in bay_names if bay_names.count(n) > 1]
        self.duplicate_bays = [b for b in self.bays if b.name in duplicate_bay_names]

    def missing_bays(self):
        """Create list of bays existing in Cloud Commerce but not STCAdmin."""
        self.missing_bays = [
            b for b in self.bays if not Bay.objects.filter(bay_id=b.id).exists()
        ]

    def excess_bays(self):
        """Create list of bays existing in STCAdmin but not Cloud Commerce."""
        bay_ids = [int(b.id) for b in self.bays]
        self.excess_bays = [b for b in Bay.objects.all() if b.bay_id not in bay_ids]

    def incorrect_bays(self):
        """
        Create list of bays with incorrect titles.

        List consists of Cloud Commerce bays for which the STCAdmin Bay with
        a matching ID does not have a matching name.
        """
        matched_bays = [
            b
            for b in self.bays
            if not any(
                [
                    b in self.duplicate_bays,
                    b in self.missing_bays,
                    b in self.excess_bays,
                ]
            )
        ]
        incorrect_bays = []
        for bay in matched_bays:
            db_bay = Bay.objects.get(bay_id=bay.id)
            bay_invalid = any(
                [bay.name != db_bay.name, bay.warehouse.id != bay.warehouse.id]
            )
            if bay_invalid:
                incorrect_bays.append(bay)
        self.incorrect_bays = incorrect_bays

    def format_bay(self, bay):
        """Return correctly formatted bay name."""
        if isinstance(bay, Bay):
            return str(bay)
        return "{} - {}".format(bay.warehouse.name, bay.name)

    def create_output(self):
        """Save bays with errors to .csv file."""
        bay_lists = [
            self.duplicate_bays,
            self.missing_bays,
            self.excess_bays,
            self.incorrect_bays,
        ]
        data = []
        for i in range(max([len(l) for l in bay_lists])):
            row = []
            for bay_list in bay_lists:
                try:
                    row.append(self.format_bay(bay_list[i]))
                except IndexError:
                    row.append("")
            data.append(row)
        output = Table(header=self.header, data=data)
        output.write(self.output_file)

    def auto_add_to_db(self):
        """Create Bays for Cloud Commerce Bays not yet in STCAdmin."""
        bays = []
        for bay in self.missing_bays:
            warehouse = Warehouse.objects.get(warehouse_id=bay.warehouse.id)
            bays.append(Bay(name=bay.name, bay_id=bay.id, warehouse=warehouse))
        Bay.objects.bulk_create(bays)

    def auto_delete_from_db(self):
        """Delete Bays from STCAdmin that do not exist in Cloud Commerce."""
        for bay in self.excess_bays:
            bay.delete()


def check_location_integrity():
    """
    Check location integrity.

    Find discrepencies between STCAdmin bay database and Cloud Commerce bays.
    Save results as .csv in media/logs.
    """
    integrity_check = LocationIntegrityCheck()
    integrity_check.create_output()
    return integrity_check


def create_backup_bay(*, bay_name, department_warehouse, backup_location):
    """
    Create a backup bay in the database and in Cloud Commerce.

    Kwargs:
        bay_name (str): The name of the new bay.
        deparment_warehouse (inventory.models.Warehouse): The warehouse for which the bay
            serves as backup.
        backup_location (inventory.models.Warehouse): The warehouse in which the bay is
            located.

    Returns:
        inventory.models.Bay

    """
    backup_bay_name = Bay.backup_bay_name(
        bay_name=bay_name,
        department=department_warehouse,
        backup_location=backup_location,
    )
    return create_bay(bay_name=backup_bay_name, warehouse=department_warehouse)


def create_bay(*, bay_name, warehouse):
    """
    Create a warehouse bay in the database and Cloud Commerce.

    Kwargs:
        bay_name (str): The name of the new bay.
        warehouse (inventory.models.Warehouse): The warehouse containing the bay.

    Returns:
        inventory.models.Bay

    """
    if Bay.objects.filter(name=bay_name).exists():
        raise ValueError(f"Bay name {bay_name} already is in use.")
    bay_id = CCAPI.get_bay_id(bay_name, warehouse.name, create=True)
    bay = Bay(bay_id=bay_id, warehouse=warehouse, name=bay_name)
    bay.save()
    return bay
