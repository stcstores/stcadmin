import datetime as dt

import pytest

from hardware import models


@pytest.fixture
def printer(printer_factory):
    return printer_factory.create()


@pytest.mark.django_db
def test_full_clean(printer):
    assert printer.full_clean() is None


# Test Attributes


@pytest.mark.django_db
def test_has_name_attribute(printer):
    assert isinstance(printer.name, str)


@pytest.mark.django_db
def test_has_manufacturer_attribute(printer):
    assert isinstance(printer.manufacturer, str)


@pytest.mark.django_db
def test_has_model_attribute(printer):
    assert isinstance(printer.model, str)


@pytest.mark.django_db
def test_has_printer_type_attribute(printer):
    assert isinstance(printer.printer_type, str)


@pytest.mark.django_db
def test_has_status_attribute(printer):
    assert isinstance(printer.status, str)


@pytest.mark.django_db
def test_has_use_attribute(printer):
    assert isinstance(printer.use, models.HardwareUse)


@pytest.mark.django_db
def test_has_storage_location_attribute(printer):
    assert isinstance(printer.storage_location, models.StorageLocation)


@pytest.mark.django_db
def test_has_notes_attribute(printer):
    assert isinstance(printer.notes, str)


@pytest.mark.django_db
def test_has_added_attribute(printer):
    assert isinstance(printer.added, dt.date)


@pytest.mark.django_db
@pytest.mark.parametrize(
    "value,display",
    (
        (models.Printer.LASER, "Laser"),
        (models.Printer.INKJET, "Inkjet"),
        (models.Printer.THERMAL, "Thermal"),
    ),
)
def test_printer_type_values(value, display, printer_factory):
    printer = printer_factory.create(printer_type=value)
    assert printer.get_printer_type_display() == display


@pytest.mark.django_db
@pytest.mark.parametrize(
    "value,display",
    (
        (models.Printer.IN_USE, "In Use"),
        (models.Printer.STORED, "Stored"),
        (models.Printer.OBSOLETE, "Obsolete"),
        (models.Printer.BINNED, "Binned"),
    ),
)
def test_status_values(value, display, printer_factory):
    printer = printer_factory.create(status=value)
    assert printer.get_status_display() == display


# Test Methods


@pytest.mark.django_db
def test_str_method(printer):
    assert str(printer) == printer.name
