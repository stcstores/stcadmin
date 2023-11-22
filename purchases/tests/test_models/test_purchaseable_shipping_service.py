import pytest

from purchases.models import PurchasableShippingService
from shipping.models import ShippingService


@pytest.fixture
def purchasable_shipping_service(purchasable_shipping_service_factory):
    return purchasable_shipping_service_factory.create()


@pytest.mark.django_db
def test_full_clean(purchasable_shipping_service):
    assert purchasable_shipping_service.full_clean() is None


# Test Attributes


@pytest.mark.django_db
def test_has_shipping_service_attribute(purchasable_shipping_service):
    assert isinstance(purchasable_shipping_service.shipping_service, ShippingService)


# Test Manager


@pytest.mark.django_db
def test_shipping_services_returns_shipping_service(purchasable_shipping_service):
    assert PurchasableShippingService.objects.shipping_services().contains(
        purchasable_shipping_service.shipping_service
    )


@pytest.mark.django_db
def test_shipping_services_does_not_return_inactive_shipping_services(
    purchasable_shipping_service_factory,
):
    purchasable_shipping_service = purchasable_shipping_service_factory.create(
        shipping_service__active=False
    )
    assert (
        PurchasableShippingService.objects.shipping_services().contains(
            purchasable_shipping_service.shipping_service
        )
        is False
    )
