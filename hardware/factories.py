"""Model factories for the hardware app."""

import datetime as dt

import factory
from factory.django import DjangoModelFactory

from hardware import models


class OperatingSystemFactory(DjangoModelFactory):
    class Meta:
        model = models.OperatingSystem

    name = factory.Faker("text", max_nb_chars=200)


class OperatingSystemInstallFactory(DjangoModelFactory):
    class Meta:
        model = models.OperatingSystemInstall

    operating_system = factory.SubFactory(OperatingSystemFactory)
    operating_system_version = factory.Faker("text", max_nb_chars=50)
    bus_width = "64"
    installation_date = factory.Faker(
        "date_time_this_decade", before_now=True, tzinfo=dt.timezone.utc
    )
    os_key = factory.Faker("text", max_nb_chars=200)


class CpuSocketFactory(DjangoModelFactory):
    class Meta:
        model = models.CpuSocket

    name = factory.Faker("text", max_nb_chars=50)
    manufacturer = models.INTEL


class CpuFactory(DjangoModelFactory):
    class Meta:
        model = models.Cpu

    manufacturer = models.INTEL
    model = factory.Faker("text", max_nb_chars=50)
    clock_speed = 2.33
    year = 2010
    generation = factory.Faker("text", max_nb_chars=50)
    socket = factory.SubFactory(CpuSocketFactory)


class GpuFactory(DjangoModelFactory):
    class Meta:
        model = models.Gpu

    manufacturer = models.INTEL
    model = factory.Faker("text", max_nb_chars=200)
    clock_speed = 2.33
    year = 2010
    vga = 1
    dvi = 1
    hdmi = 1
    display_port = 0


class MotherboardFactory(DjangoModelFactory):
    class Meta:
        model = models.Motherboard

    manufacturer = models.INTEL
    model = factory.Faker("text", max_nb_chars=50)
    socket = factory.SubFactory(CpuSocketFactory)
    chipset = factory.Faker("text", max_nb_chars=50)
    vga = 1
    dvi = 1
    hdmi = 1
    display_port = 0


class HardwareUseFactory(DjangoModelFactory):
    class Meta:
        model = models.HardwareUse

    name = factory.Faker("text", max_nb_chars=200)
    location = factory.Faker("text", max_nb_chars=200)
    primary_user = factory.Faker("text", max_nb_chars=200)
    primary_use = factory.Faker("text", max_nb_chars=200)


class StorageLocationFactory(DjangoModelFactory):
    class Meta:
        model = models.StorageLocation

    name = factory.Faker("text", max_nb_chars=200)


class ComputerFactory(DjangoModelFactory):
    class Meta:
        model = models.Computer

    name = factory.Faker("text", max_nb_chars=200)
    computer_type = models.Computer.DESKTOP
    network_name = factory.Faker("text", max_nb_chars=200)
    status = models.Computer.IN_USE
    operating_system = factory.SubFactory(OperatingSystemInstallFactory)
    motherboard = factory.SubFactory(MotherboardFactory)
    cpu = factory.SubFactory(CpuFactory)
    ram_gb = 16
    gpu = factory.SubFactory(GpuFactory)
    use = factory.SubFactory(HardwareUseFactory)
    storage_location = factory.SubFactory(StorageLocationFactory)
    notes = factory.Faker("text", max_nb_chars=200)
    added = factory.Faker(
        "date_time_this_decade", before_now=True, tzinfo=dt.timezone.utc
    )


class PrinterFactory(DjangoModelFactory):
    class Meta:
        model = models.Printer

    name = factory.Faker("text", max_nb_chars=200)
    manufacturer = factory.Faker("text", max_nb_chars=50)
    model = factory.Faker("text", max_nb_chars=50)
    printer_type = models.Printer.LASER
    status = models.Printer.IN_USE
    use = factory.SubFactory(HardwareUseFactory)
    storage_location = factory.SubFactory(StorageLocationFactory)
    notes = factory.Faker("text", max_nb_chars=200)
    added = factory.Faker(
        "date_time_this_decade", before_now=True, tzinfo=dt.timezone.utc
    )


class NameFactory(DjangoModelFactory):
    class Meta:
        model = models.Name

    name = factory.Faker("text", max_nb_chars=50)
    is_available = True


class ComputerMaintainanceJobFactory(DjangoModelFactory):
    class Meta:
        model = models.ComputerMaintainanceJob

    completed_at = factory.Faker(
        "date_time_this_decade", before_now=True, tzinfo=dt.timezone.utc
    )
    computer = factory.SubFactory(ComputerFactory)
    cleaned = True
    os_reinstalled = True
    notes = factory.Faker("text", max_nb_chars=50)
