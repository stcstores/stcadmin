import pytest

from hardware import models


@pytest.fixture
def cpu(cpu_factory):
    return cpu_factory.create()


@pytest.mark.django_db
def test_full_clean(cpu):
    assert cpu.full_clean() is None


# Test Attributes


@pytest.mark.django_db
def test_has_manufacturer_attribute(cpu):
    assert isinstance(cpu.manufacturer, str)


@pytest.mark.django_db
def test_has_model_attribute(cpu):
    assert isinstance(cpu.model, str)


@pytest.mark.django_db
def test_has_clock_speed_attribute(cpu):
    assert isinstance(cpu.clock_speed, float)


@pytest.mark.django_db
def test_has_year_attribute(cpu):
    assert isinstance(cpu.year, int)


@pytest.mark.django_db
def test_has_generation_attribute(cpu):
    assert isinstance(cpu.generation, str)


@pytest.mark.django_db
def test_has_socket_attribute(cpu):
    assert isinstance(cpu.socket, models.CpuSocket)


@pytest.mark.django_db
@pytest.mark.parametrize(
    "value,display", ((models.INTEL, "Intel"), (models.AMD, "AMD"))
)
def test_manufacturer_values(value, display, cpu_factory):
    cpu = cpu_factory.create(manufacturer=value)
    assert cpu.get_manufacturer_display() == display


# Test Methods


@pytest.mark.django_db
def test_str_method(cpu_factory):
    cpu = cpu_factory.create(manufacturer=models.INTEL, model="i7")
    assert str(cpu) == "Intel i7"
