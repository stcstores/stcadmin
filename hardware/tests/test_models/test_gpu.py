import pytest

from hardware import models


@pytest.fixture
def gpu(gpu_factory):
    return gpu_factory.create()


@pytest.mark.django_db
def test_full_clean(gpu):
    assert gpu.full_clean() is None


# Test Attributes


@pytest.mark.django_db
def test_has_manufacturer_attribute(gpu):
    assert isinstance(gpu.manufacturer, str)


@pytest.mark.django_db
def test_has_model_attribute(gpu):
    assert isinstance(gpu.model, str)


@pytest.mark.django_db
def test_has_clock_speed_attribute(gpu):
    assert isinstance(gpu.clock_speed, float)


@pytest.mark.django_db
def test_has_year_attribute(gpu):
    assert isinstance(gpu.year, int)


@pytest.mark.django_db
def test_has_vga_attribute(gpu):
    assert isinstance(gpu.vga, int)


@pytest.mark.django_db
def test_has_dvi_attribute(gpu):
    assert isinstance(gpu.dvi, int)


@pytest.mark.django_db
def test_has_hdmi_attribute(gpu):
    assert isinstance(gpu.hdmi, int)


@pytest.mark.django_db
def test_has_display_port_attribute(gpu):
    assert isinstance(gpu.display_port, int)


@pytest.mark.django_db
@pytest.mark.parametrize(
    "value,display",
    ((models.INTEL, "Intel"), (models.AMD, models.AMD), (models.NVIDIA, models.NVIDIA)),
)
def test_manufacturer_values(value, display, gpu_factory):
    gpu = gpu_factory.create(manufacturer=value)
    assert gpu.get_manufacturer_display() == display


# Test Methods


@pytest.mark.django_db
def test_str_method(gpu_factory):
    gpu = gpu_factory.create(manufacturer=models.NVIDIA, model="GTX 3080")
    assert str(gpu) == "NVIDIA GTX 3080"
