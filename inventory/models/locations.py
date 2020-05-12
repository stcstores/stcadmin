"""Models for storing Warehouse Bay Locations."""


import os
import sys

from ccapi import CCAPI
from django.conf import settings
from django.core.exceptions import ValidationError
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
        return self.bay_set.exclude(is_default=True)

    @property
    def default_bay(self):
        """Return the default bay for this warehouse."""
        return self.bay_set.get(is_default=True)


class BayManager(models.Manager):
    """Manager for the inventory.Bay model."""

    def new_bay(self, name, warehouse):
        """
        Create a new bay in Cloud Commerce.

        Kwargs:
            name (str): The name of the new bay.
            warehouse (inventory.models.Warehouse): The warehouse to which the bay
                will belong.

        Returns:
            inventory.Bay

        Raises:
            ValidationError: If a Bay already exists with a matching name.

        """
        if self.get_queryset().filter(name=name).exists():
            raise ValidationError(f"A Bay named {name} already exists.")
        bay_ID = self._create_bay_in_cloud_commerce(
            name=name, warehouse_id=warehouse.warehouse_ID
        )
        bay = Bay(bay_ID=bay_ID, name=name, warehouse=warehouse)
        bay.save()
        return bay

    def new_backup_bay(self, name, department, backup_location):
        """
        Return a new backup bay in Cloud Commerce.

        Kwargs:
            name (str): The name of the new bay.
            department (inventory.models.Warehouse): The default warehouse of the
                department to which products in this bay belong.
            backup_location (inventory.models.Warehouse): The Warehouse representing
                the physical location of the bay.

        Returns:
            inventory.Bay

        Raises:
            ValidationError: If a Bay already exists with a matching name.


        """
        backup_name = self.backup_bay_name(
            name=name, department=department, backup_location=backup_location
        )
        return self.new_bay(name=backup_name, warehouse=department)

    def _create_bay_in_cloud_commerce(self, name, warehouse_id):
        """
        Create a new bay in Cloud Commerce.

        Args:
            name (str): The name of the bay.
            warehouse_id (str): The Cloud Commerce ID of the warehouse to which the bay
                will be added.

        Returns:
            (str): The ID of the newly created bay.

        """
        try:
            bay_ID = CCAPI.add_bay_to_warehouse(bay=name, warehouse_id=warehouse_id)
        except Exception:
            raise Exception("Error creating new bay in Cloud Commerce")
        if bay_ID is None:
            raise Exception("Error creating new bay in Cloud Commerce")
        return str(bay_ID)

    def backup_bay_name(self, *, name, department, backup_location):
        """Return the name for a backup bay."""
        return f"{department.abriviation} Backup {backup_location.name} {name}"


class NonDefaultBaysManager(BayManager):
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
    is_default = models.BooleanField(default=False)

    objects = BayManager()
    non_default = NonDefaultBaysManager()

    class Meta:
        """Meta class for Bay."""

        verbose_name = "Bay"
        verbose_name_plural = "Bays"
        ordering = ("-is_default", "name")
        constraints = [
            models.UniqueConstraint(
                fields=["warehouse"],
                condition=models.Q(is_default=True),
                name="single_default_bay_per_warehouse",
            )
        ]

    def __str__(self):
        return "{} - {}".format(self.warehouse, self.name)

    @property
    def is_backup(self):
        """Return True if the bay is a backup bay, otherwise False."""
        return "Backup" in self.name

    @property
    def is_primary(self):
        """Return True if the bay is a primary bay, otherwise False."""
        if not self.is_backup and not self.is_default:
            return True
        return False


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
        for i in range(max([len(_) for _ in bay_lists])):
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
