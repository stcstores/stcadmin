import datetime as dt

import pytest

from hardware.models import OperatingSystem


@pytest.fixture
def operating_system_install(operating_system_install_factory):
    return operating_system_install_factory.create()


@pytest.mark.django_db
def test_full_clean(operating_system_install):
    assert operating_system_install.full_clean() is None


# Test Attributes


@pytest.mark.django_db
def test_has_operating_system_attribute(operating_system_install):
    assert isinstance(operating_system_install.operating_system, OperatingSystem)


@pytest.mark.django_db
def test_has_operating_system_version_attribute(operating_system_install):
    assert isinstance(operating_system_install.operating_system_version, str)


@pytest.mark.django_db
def test_has_bus_width_attribute(operating_system_install):
    assert isinstance(operating_system_install.bus_width, str)


@pytest.mark.django_db
def test_has_installation_date_attribute(operating_system_install):
    assert isinstance(operating_system_install.installation_date, dt.date)


@pytest.mark.django_db
def test_has_os_key_attribute(operating_system_install):
    assert isinstance(operating_system_install.os_key, str)


@pytest.mark.django_db
@pytest.mark.parametrize("value,display", (("64", "64 Bit"), ("32", "32 Bit")))
def test_bus_width_values(value, display, operating_system_install_factory):
    os_install = operating_system_install_factory.create(bus_width=value)
    assert os_install.get_bus_width_display() == display


# Test Methods


@pytest.mark.django_db
def test_str_method(operating_system_install_factory):
    operating_system_install = operating_system_install_factory.create(
        operating_system__name="Windows 10",
        operating_system_version="Home",
        bus_width="64",
    )
    assert str(operating_system_install) == "Windows 10 Home 64"
