import pytest

from itd import models


@pytest.mark.django_db
def test_itd_id(itd_order_factory):
    order = itd_order_factory.create()
    assert order.itd_id() == models.itd_order_id(order.order_id)


@pytest.mark.django_db
def test_create_from_dispatch_order_sets_manifest(mock_orders, itd_manifest_factory):
    manifest = itd_manifest_factory.create()
    order = models.ITDOrder.objects.create_from_dispatch_order(manifest, mock_orders[0])
    order.refresh_from_db()
    assert order.manifest == manifest


@pytest.mark.django_db
def test_create_from_dispatch_order_sets_order_id(mock_orders, itd_manifest_factory):
    manifest = itd_manifest_factory.create()
    order = models.ITDOrder.objects.create_from_dispatch_order(manifest, mock_orders[0])
    order.refresh_from_db()
    assert order.order_id == str(mock_orders[0].order_id)


@pytest.mark.django_db
def test_create_from_dispatch_order_sets_customer_id(mock_orders, itd_manifest_factory):
    manifest = itd_manifest_factory.create()
    order = models.ITDOrder.objects.create_from_dispatch_order(manifest, mock_orders[0])
    order.refresh_from_db()
    assert order.customer_id == str(mock_orders[0].customer_id)


@pytest.mark.django_db
def test_create_from_dispatch_order_creates_products(mock_orders, itd_manifest_factory):
    manifest = itd_manifest_factory.create()
    order = models.ITDOrder.objects.create_from_dispatch_order(manifest, mock_orders[0])
    order.refresh_from_db()
    for product in mock_orders[0].products:
        assert models.ITDProduct.objects.filter(order=order, sku=product.sku).exists()
