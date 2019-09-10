"""Models for storing Warehouse Bay Locations."""


from ccapi import CCAPI
from django.db import models


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
        return self.bay_set.get(is_default=True)


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
    is_default = models.BooleanField(default=False)

    objects = models.Manager()
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
