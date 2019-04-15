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
        return super().get_queryset().exclude(warehouse_ID=5610)


class Warehouse(models.Model):
    """Model for Warehouses."""

    warehouse_ID = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=255, unique=True)
    abriviation = models.CharField(max_length=4, null=True, blank=True, unique=True)

    objects = models.Manager()
    used_warehouses = UsedWarehouseManager()

    class Meta:
        """Meta class for Warehouse."""

        verbose_name = "Warehouse"
        verbose_name_plural = "Warehouses"
        ordering = ("name",)

    def __str__(self):
        return self.name

    @staticmethod
    def get_cc_warehouses():
        """Return the Cloud Commerce Warehouses."""
        return CCAPI.get_warehouses()

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

    bay_ID = models.CharField(max_length=255, unique=True)
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
    def default(self):
        """Return True if the bay is the default bay for it's warehouse."""
        return self.name == self.warehouse.name

    @staticmethod
    def backup_bay_name(*, bay_name, department, backup_location):
        """Return the name for a backup bay."""
        return f"{department.abriviation} Backup {backup_location.name} {bay_name}"

    @classmethod
    def new_backup_bay(cls, name, department, backup_location):
        """Return a new Bay instance named as a backup bay."""
        backup_name = cls.backup_bay_name(
            bay_name=name, department=department, backup_location=backup_location
        )
        return cls(name=backup_name, warehouse=department)

    def save(self, *args, **kwargs):
        """Create the bay in Cloud Commerce if it has no ID."""
        if not self.bay_ID:
            self.bay_ID = self.get_CC_ID()
        super().save(*args, **kwargs)

    def get_CC_ID(self):
        """
        Return the Cloud Commerce ID for this bay.

        If it does not exist in Cloud Commerce it will be created.
        """
        bay_ID = CCAPI.get_bay_id(self.name, self.warehouse.name, create=True)
        if bay_ID:
            return bay_ID
        else:
            raise Exception("Error creating new bay in Cloud Commerce")


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
            b for b in self.bays if not Bay.objects.filter(bay_ID=b.id).exists()
        ]

    def excess_bays(self):
        """Create list of bays existing in STCAdmin but not Cloud Commerce."""
        bay_IDs = [int(b.id) for b in self.bays]
        self.excess_bays = [b for b in Bay.objects.all() if b.bay_ID not in bay_IDs]

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
            db_bay = Bay.objects.get(bay_ID=bay.id)
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
            warehouse = Warehouse.objects.get(warehouse_ID=bay.warehouse.id)
            bays.append(Bay(name=bay.name, bay_ID=bay.id, warehouse=warehouse))
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
