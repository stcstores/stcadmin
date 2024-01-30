import pytest

from hardware import models


@pytest.fixture
def motherboard(motherboard_factory):
    return motherboard_factory.create()


@pytest.mark.django_db
def test_full_clean(motherboard):
    assert motherboard.full_clean() is None


# Test Attributes


@pytest.mark.django_db
def test_has_manufacturer_attribute(motherboard):
    assert isinstance(motherboard.manufacturer, str)


@pytest.mark.django_db
def test_has_model_attribute(motherboard):
    assert isinstance(motherboard.model, str)


@pytest.mark.django_db
def test_has_socket_attribute(motherboard):
    assert isinstance(motherboard.socket, models.CpuSocket)


@pytest.mark.django_db
def test_has_chipset_attribute(motherboard):
    assert isinstance(motherboard.chipset, str)


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


# Test Methods


@pytest.mark.django_db
def test_str_method(motherboard_factory):
    motherboard = motherboard_factory.create(manufacturer="Asus", model="Z97")
    assert str(motherboard) == "Asus Z97"
