import pytest
from django.urls import reverse

from fba import models


@pytest.fixture
def shipment_order(fba_shipment_order_factory):
    return fba_shipment_order_factory.create()


@pytest.fixture
def shipment_package(shipment_order, fba_shipment_package_factory):
    return fba_shipment_package_factory.create(shipment_order=shipment_order)


@pytest.fixture
def shipment_item(shipment_package, fba_shipment_item_factory):
    return fba_shipment_item_factory.create(package=shipment_package)


@pytest.fixture
def url(shipment_order, shipment_item):
    return reverse("fba:delete_shipment", args=[shipment_order.pk])


@pytest.fixture
def get_response(group_logged_in_client, url):
    return group_logged_in_client.get(url)


@pytest.fixture
def post_response(group_logged_in_client, url):
    return group_logged_in_client.post(url, {})


@pytest.mark.django_db
def test_uses_template(get_response):
    assert "fba/shipments/confirm_delete_shipment.html" in (
        t.name for t in get_response.templates
    )


@pytest.mark.django_db
def test_status_code(get_response):
    assert get_response.status_code == 200


@pytest.mark.django_db
def test_get_without_group(logged_in_client, url):
    assert logged_in_client.get(url).status_code == 403


@pytest.mark.django_db
def test_post_without_group(logged_in_client, url):
    assert logged_in_client.post(url, {}).status_code == 403


@pytest.mark.django_db
def test_shipment_order_in_context(get_response, shipment_order):
    assert get_response.context["object"] == shipment_order


@pytest.mark.django_db
def test_deletes_shipment_order(
    post_response, shipment_order, shipment_package, shipment_item
):
    assert (
        models.FBAShipmentOrder.objects.filter(id=shipment_order.id).exists() is False
    )
    assert (
        models.FBAShipmentPackage.objects.filter(id=shipment_package.id).exists()
        is False
    )
    assert models.FBAShipmentItem.objects.filter(id=shipment_item.id).exists() is False


@pytest.mark.django_db
def test_redirects(post_response):
    assert post_response.status_code == 302
    assert post_response["Location"] == reverse("fba:shipments")
