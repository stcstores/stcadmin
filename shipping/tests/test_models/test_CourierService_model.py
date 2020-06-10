import pytest

from shipping import models


@pytest.fixture
def courier_service_ID():
    return "746"


@pytest.fixture
def name():
    return "Test Courier Service"


@pytest.fixture
def courier(courier_factory):
    return courier_factory.create()


@pytest.fixture
def new_courier_service(courier_service_ID, name, courier):
    courier = models.CourierService(
        courier_service_ID=courier_service_ID, name=name, courier=courier
    )
    courier.save()
    return courier


@pytest.mark.django_db
def test_courier_service_ID_is_set(courier_service_ID, new_courier_service):
    assert new_courier_service.courier_service_ID == courier_service_ID


@pytest.mark.django_db
def test_name_is_set(name, new_courier_service):
    assert new_courier_service.name == name


@pytest.mark.django_db
def test_courier_is_set(courier, new_courier_service):
    assert new_courier_service.courier == courier


@pytest.mark.django_db
def test_inactive_is_set(new_courier_service):
    assert new_courier_service.inactive is False


@pytest.mark.django_db
def test_str_method(courier_service_factory):
    courier_service = courier_service_factory.create()
    assert (
        str(courier_service)
        == f"{courier_service.courier_service_ID}: {courier_service.name}"
    )
