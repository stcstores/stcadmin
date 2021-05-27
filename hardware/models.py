"""Models for the Hardware app."""

import random

from django.db import models

INTEL = "Intel"
AMD = "AMD"
CPU_MANUFACTURERS = ((INTEL, "Intel"), (AMD, "AMD"))


class OperatingSystem(models.Model):
    """Model for operating systems."""

    name = models.CharField(max_length=255, unique=True)

    class Meta:
        """Meta class for OperatingSystem."""

        verbose_name = "Operating System"
        verbose_name_plural = "Operating Systems"
        ordering = ["name"]

    def __str__(self):
        return self.name


class OperatingSystemInstall(models.Model):
    """Model for operating system installs."""

    BUS_WIDTH = (("64", "64 Bit"), ("32", "32 Bit"))
    operating_system = models.ForeignKey(OperatingSystem, on_delete=models.CASCADE)
    operating_system_version = models.CharField(max_length=50)
    bus_width = models.CharField(max_length=50, choices=BUS_WIDTH)
    installation_date = models.DateField()
    os_key = models.CharField(max_length=255, blank=True)

    class Meta:
        """Meta class for OperatingSystemInstall."""

        verbose_name = "Operating System Install"
        verbose_name_plural = "Operating System Installs"

    def __str__(self):
        return (
            f"{self.operating_system} {self.operating_system_version} {self.bus_width}"
        )


class CpuSocket(models.Model):
    """Model for CPU sockets."""

    name = models.CharField(max_length=50, unique=True)
    manufacturer = models.CharField(max_length=50, choices=CPU_MANUFACTURERS)

    class Meta:
        """Meta class for CpuSocket."""

        verbose_name = "CPU Socket"
        verbose_name_plural = "CPU Sockets"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Cpu(models.Model):
    """Model for CPUs."""

    manufacturer = models.CharField(max_length=50, choices=CPU_MANUFACTURERS)
    model = models.CharField(max_length=255)
    clock_speed = models.FloatField()
    year = models.IntegerField()
    generation = models.CharField(max_length=50, blank=True)
    socket = models.ForeignKey(CpuSocket, on_delete=models.CASCADE)

    class Meta:
        """Meta class for Cpu."""

        verbose_name = "CPU"
        verbose_name_plural = "CPUs"
        unique_together = ("manufacturer", "model")
        ordering = ["manufacturer", "model"]

    def __str__(self):
        return f"{self.manufacturer} {self.model}"


class Gpu(models.Model):
    """Model for GPUs."""

    manufacturer = models.CharField(max_length=50, choices=CPU_MANUFACTURERS)
    model = models.CharField(max_length=255)
    clock_speed = models.FloatField()
    year = models.SmallIntegerField()
    vga = models.SmallIntegerField(default=0)
    dvi = models.SmallIntegerField(default=0)
    hdmi = models.SmallIntegerField(default=0)
    display_port = models.SmallIntegerField(default=0)

    class Meta:
        """Meta class for Gpu."""

        verbose_name = "GPU"
        verbose_name_plural = "GPUs"
        unique_together = ("manufacturer", "model")
        ordering = ["manufacturer", "model"]

    def __str__(self):
        return f"{self.manufacturer} {self.model}"


class Motherboard(models.Model):
    """Model for motherboards."""

    manufacturer = models.CharField(max_length=50)
    model = models.CharField(max_length=50)
    socket = models.ForeignKey(CpuSocket, on_delete=models.CASCADE)
    chipset = models.CharField(max_length=50)
    vga = models.SmallIntegerField(default=0)
    dvi = models.SmallIntegerField(default=0)
    hdmi = models.SmallIntegerField(default=0)
    display_port = models.SmallIntegerField(default=0)

    class Meta:
        """Meta class for Motherboard."""

        verbose_name = "Motherboard"
        verbose_name_plural = "Motherboards"
        unique_together = ("manufacturer", "model")
        ordering = ["manufacturer", "model"]

    def __str__(self):
        return f"{self.manufacturer} {self.model}"


class HardwareUse(models.Model):
    """Model for computer uses."""

    name = models.CharField(max_length=200, unique=True)
    location = models.CharField(max_length=200)
    primary_user = models.CharField(max_length=200, blank=True)
    primary_use = models.TextField(blank=True)

    class Meta:
        """Meta class for HardwareUse."""

        verbose_name = "Hardware Use"
        verbose_name_plural = "Hardware Uses"

    def __str__(self):
        return self.name


class StorageLocation(models.Model):
    """Model for hardware storage locations."""

    name = models.CharField(max_length=200, unique=True)

    class Meta:
        """Meta class for StorageLocation."""

        verbose_name = "Stoarage Location"
        verbose_name_plural = "Storage Locations"

    def __str__(self):
        return self.name


class Computer(models.Model):
    """Model for computers."""

    IN_USE = "in_use"
    STORED = "stored"
    OBSOLETE = "obsolete"
    BINNED = "binned"

    STATUSES = (
        (IN_USE, "In Use"),
        (STORED, "Stored"),
        (OBSOLETE, "Obsolete"),
        (BINNED, "Binned"),
    )

    DESKTOP = "desktop"
    LAPTOP = "laptop"
    TABLET = "tablet"

    TYPES = ((DESKTOP, "Desktop"), (LAPTOP, "Laptop"), (TABLET, "Tablet"))

    name = models.CharField(max_length=255, unique=True)
    computer_type = models.CharField(max_length=50, choices=TYPES)
    network_name = models.CharField(max_length=255)
    status = models.CharField(max_length=50, choices=STATUSES)
    operating_system = models.ForeignKey(
        OperatingSystemInstall, blank=True, null=True, on_delete=models.CASCADE
    )
    motherboard = models.ForeignKey(
        Motherboard, blank=True, null=True, on_delete=models.CASCADE
    )
    cpu = models.ForeignKey(Cpu, blank=True, null=True, on_delete=models.CASCADE)
    ram_gb = models.SmallIntegerField()
    gpu = models.ForeignKey(Gpu, blank=True, null=True, on_delete=models.CASCADE)
    use = models.ForeignKey(
        HardwareUse, blank=True, null=True, on_delete=models.CASCADE
    )
    storage_location = models.ForeignKey(
        StorageLocation, blank=True, null=True, on_delete=models.CASCADE
    )
    notes = models.TextField(blank=True)
    added = models.DateField(auto_now_add=True)

    class Meta:
        """Meta class for Computer."""

        verbose_name = "Computer"
        verbose_name_plural = "Computers"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Printer(models.Model):
    """Model for printers."""

    IN_USE = "in_use"
    STORED = "stored"
    OBSOLETE = "obsolete"
    BINNED = "binned"

    STATUSES = (
        (IN_USE, "In Use"),
        (STORED, "Stored"),
        (OBSOLETE, "Obsolete"),
        (BINNED, "Binned"),
    )

    LASER = "laser"
    INKJET = "inkjet"
    THERMAL = "thermal"

    TYPES = ((LASER, "Laser"), (INKJET, "Inkjet"), (THERMAL, "Thermal"))

    name = models.CharField(max_length=255, unique=True)
    manufacturer = models.CharField(max_length=50)
    model = models.CharField(max_length=50)
    printer_type = models.CharField(max_length=50, choices=TYPES)
    status = models.CharField(max_length=50, choices=STATUSES)
    use = models.ForeignKey(
        HardwareUse, blank=True, null=True, on_delete=models.CASCADE
    )
    storage_location = models.ForeignKey(
        StorageLocation, blank=True, null=True, on_delete=models.CASCADE
    )
    notes = models.TextField(blank=True)
    added = models.DateField(auto_now_add=True)

    class Meta:
        """Meta class for Printer."""

        verbose_name = "Printer"
        verbose_name_plural = "Printers"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Name(models.Model):
    """Model for hardware names."""

    name = models.CharField(max_length=50, unique=True)
    is_available = models.BooleanField(default=True)

    class Meta:
        """Meta class for Name."""

        verbose_name = "Name"
        verbose_name_plural = "Names"
        ordering = ["-is_available", "name"]

    class Available(models.Manager):
        """Manager for unused names."""

        def get_queryset(self):
            """Return a queryset of unused names."""
            return super().get_queryset().filter(is_available=True)

        def get_name(self):
            """Return a random unused name."""
            name = random.choice(self.get_queryset())
            return name

    objects = models.Manager()
    available = Available()

    def __str__(self):
        return self.name

    def network_safe(self):
        """Return the name in a network safe format."""
        return self.name.upper().replace(" ", "_")

    def use(self):
        """Mark the name used."""
        self.is_available = False
        self.save()


class ComputerMaintainanceJob(models.Model):
    """Model for computer maintainance jobs."""

    completed_at = models.DateTimeField()
    computer = models.ForeignKey(Computer, on_delete=models.CASCADE)
    cleaned = models.BooleanField()
    os_reinstalled = models.BooleanField()
    notes = models.TextField(blank=True)

    class Meta:
        """Meta class for ComputerMaintainanceJob."""

        verbose_name = "Computer Maintainance Job"
        verbose_name_plural = "Computer Maintainance Jobs"
        ordering = ["completed_at"]

    def __str__(self):
        return f"{self.computer.name} on {self.completed_at.strftime('%d %B %Y')}"
