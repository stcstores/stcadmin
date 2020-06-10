import pytest

from shipping import models


@pytest.fixture
def courier_ID():
    return "164816"


@pytest.fixture
def name():
    return "Test Courier"


@pytest.fixture
def courier_type(courier_type_factory):
    return courier_type_factory.create()


@pytest.fixture
def new_courier(courier_ID, name, courier_type):
    courier = models.Courier(
        courier_ID=courier_ID, name=name, courier_type=courier_type
    )
    courier.save()
    return courier


@pytest.mark.django_db
def test_courier_ID_is_set(courier_ID, new_courier):
    assert new_courier.courier_ID == courier_ID


@pytest.mark.django_db
def test_name_is_set(name, new_courier):
    assert new_courier.name == name


@pytest.mark.django_db
def test_courier_type_is_set(courier_type, new_courier):
    assert new_courier.courier_type == courier_type


@pytest.mark.django_db
def test_inactive_is_set(new_courier):
    assert new_courier.inactive is False


@pytest.mark.django_db
def test_str_method(courier_factory):
    courier = courier_factory.create()
    assert str(courier) == f"{courier.courier_ID}: {courier.name}"
