import pytest

from shipping import models


@pytest.fixture
def courier_type_ID():
    return "6846"


@pytest.fixture
def name():
    return "Test Courier Type"


@pytest.fixture
def provider(provider_factory):
    return provider_factory.create()


@pytest.fixture
def new_courier_type(courier_type_ID, name, provider):
    courier_type = models.CourierType(
        courier_type_ID=courier_type_ID, name=name, provider=provider
    )
    courier_type.save()
    return courier_type


@pytest.mark.django_db
def test_courier_type_ID_is_set(courier_type_ID, new_courier_type):
    assert new_courier_type.courier_type_ID == courier_type_ID


@pytest.mark.django_db
def test_name_is_set(name, new_courier_type):
    assert new_courier_type.name == name


@pytest.mark.django_db
def test_provider_is_set(provider, new_courier_type):
    assert new_courier_type.provider == provider


@pytest.mark.django_db
def test_inactive_is_set(new_courier_type):
    assert new_courier_type.inactive is False


@pytest.mark.django_db
def test_str_method(courier_type_factory):
    courier_type = courier_type_factory.create()
    assert str(courier_type) == courier_type.name
