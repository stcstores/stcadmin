import datetime as dt

import pytest

from hardware import models


@pytest.fixture
def computer(computer_factory):
    return computer_factory.create()


@pytest.mark.django_db
def test_full_clean(computer):
    assert computer.full_clean() is None


# Test Attributes


@pytest.mark.django_db
def test_has_name_attribute(computer):
    assert isinstance(computer.name, str)


@pytest.mark.django_db
def test_has_computer_type_attribute(computer):
    assert isinstance(computer.computer_type, str)


@pytest.mark.django_db
def test_has_network_name_attribute(computer):
    assert isinstance(computer.network_name, str)


@pytest.mark.django_db
def test_has_status_attribute(computer):
    assert isinstance(computer.status, str)


@pytest.mark.django_db
def test_has_operating_system_attribute(computer):
    assert isinstance(computer.operating_system, models.OperatingSystemInstall)


@pytest.mark.django_db
def test_has_motherboard_attribute(computer):
    assert isinstance(computer.motherboard, models.Motherboard)


@pytest.mark.django_db
def test_has_cpu_attribute(computer):
    assert isinstance(computer.cpu, models.Cpu)


@pytest.mark.django_db
def test_has_ram_gb_attribute(computer):
    assert isinstance(computer.ram_gb, int)


@pytest.mark.django_db
def test_has_gpu_attribute(computer):
    assert isinstance(computer.gpu, models.Gpu)


@pytest.mark.django_db
def test_has_use_attribute(computer):
    assert isinstance(computer.use, models.HardwareUse)


@pytest.mark.django_db
def test_has_storage_location_attribute(computer):
    assert isinstance(computer.storage_location, models.StorageLocation)


@pytest.mark.django_db
def test_has_notes_attribute(computer):
    assert isinstance(computer.notes, str)


@pytest.mark.django_db
def test_has_added_attribute(computer):
    assert isinstance(computer.added, dt.date)


@pytest.mark.django_db
@pytest.mark.parametrize(
    "value,display",
    (
        (models.Computer.DESKTOP, "Desktop"),
        (models.Computer.LAPTOP, "Laptop"),
        (models.Computer.TABLET, "Tablet"),
    ),
)
def test_computer_type_values(value, display, computer_factory):
    computer = computer_factory.create(computer_type=value)
    assert computer.get_computer_type_display() == display


@pytest.mark.django_db
@pytest.mark.parametrize(
    "value,display",
    (
        (models.Computer.IN_USE, "In Use"),
        (models.Computer.STORED, "Stored"),
        (models.Computer.OBSOLETE, "Obsolete"),
        (models.Computer.BINNED, "Binned"),
    ),
)
def test_status_values(value, display, computer_factory):
    computer = computer_factory.create(status=value)
    assert computer.get_status_display() == display


# Test Methods


@pytest.mark.django_db
def test_str_method(computer):
    assert str(computer) == computer.name
