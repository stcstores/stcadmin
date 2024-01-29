import pytest

from hardware import models


@pytest.fixture
def cpu_socket(cpu_socket_factory):
    return cpu_socket_factory.create()


@pytest.mark.django_db
def test_full_clean(cpu_socket):
    assert cpu_socket.full_clean() is None


# Test Attributes


@pytest.mark.django_db
def test_has_name_attribute(cpu_socket):
    assert isinstance(cpu_socket.name, str)


@pytest.mark.django_db
def test_has_manufacturer_attribute(cpu_socket):
    assert isinstance(cpu_socket.manufacturer, str)


@pytest.mark.django_db
@pytest.mark.parametrize(
    "value,display", ((models.INTEL, "Intel"), (models.AMD, "AMD"))
)
def test_manufacturer_values(value, display, cpu_socket_factory):
    os_install = cpu_socket_factory.create(manufacturer=value)
    assert os_install.get_manufacturer_display() == display


# Test Methods


@pytest.mark.django_db
def test_str_method(cpu_socket):
    assert str(cpu_socket) == cpu_socket.name
