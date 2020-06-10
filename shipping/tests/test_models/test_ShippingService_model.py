import pytest

from shipping import models


@pytest.fixture
def name():
    return "Test Shipping Service"


@pytest.fixture
def new_shipping_service(name):
    shipping_service = models.ShippingService(name=name)
    shipping_service.save()
    return shipping_service


@pytest.mark.django_db
def test_sets_name(new_shipping_service, name):
    assert new_shipping_service.name == name


@pytest.mark.django_db
def test__str__method(shipping_service_factory, name):
    assert str(shipping_service_factory.build(name=name)) == name


@pytest.mark.django_db
def test_name_is_unique(name, shipping_service_factory):
    shipping_service_factory.create(name=name)
    with pytest.raises(Exception):
        shipping_service_factory.create(name=name)
