import tempfile
from datetime import datetime
from unittest.mock import call, patch

import pytest
from django.test import override_settings
from django.utils import timezone

from itd import models
from itd.models import ITDManifest


@pytest.fixture
def new_manifest():
    manifest = ITDManifest()
    manifest.save()
    return manifest


@pytest.fixture
def country(country_factory):
    return country_factory.create(country_ID=1, name="United Kindom")


@pytest.fixture
def mock_get_orders_error(mock_CCAPI):
    mock_CCAPI.get_orders_for_dispatch.side_effect = Exception()


@pytest.fixture
def shipping_rules(shipping_rule_factory):
    return [shipping_rule_factory.create() for _ in range(10)]


@pytest.fixture
def itd_shipping_rules(shipping_rules):
    indexes = (0, 3, 6, 8)
    return [shipping_rules[index] for index in indexes]


@pytest.fixture
def itd_config(itd_shipping_rules):
    config = models.ITDConfig.get_solo()
    config.shipping_rules.set(itd_shipping_rules)
    config.save()
    return config


@pytest.fixture
def itd_config_single_rule(itd_shipping_rules):
    config = models.ITDConfig.get_solo()
    config.shipping_rules.set([itd_shipping_rules[0]])
    config.save()
    return config


@pytest.mark.django_db
def test_default_create_at_attribute(mock_now, new_manifest):
    assert new_manifest.created_at == mock_now


@pytest.mark.django_db
def test_last_generated_at_attributes(mock_now, new_manifest):
    assert new_manifest.last_generated_at is None


@pytest.mark.django_db
def test_status_attribute(new_manifest):
    assert new_manifest.status == ITDManifest.OPEN


@pytest.mark.django_db
def test_manifest_file_attributs(new_manifest):
    assert bool(new_manifest.manifest_file) is False


@pytest.mark.django_db
def test_manifest_ordering(itd_manifest_factory):
    dates = [
        timezone.make_aware(datetime(*date))
        for date in ((2020, 5, 13), (2019, 12, 15), (2020, 1, 16))
    ]
    for date in dates:
        itd_manifest_factory.create(created_at=date)
    manifests = ITDManifest.objects.all()
    assert list(manifests) == sorted(
        list(manifests), key=lambda x: x.created_at, reverse=True
    )


@pytest.mark.django_db
def test_close_manifest():
    with patch("itd.models.ITDManifest.objects.close_manifest") as mock_close_manifest:
        manifest = models.ITDManifest.objects.create_manifest()
    mock_close_manifest.assert_called_once_with(manifest.id)


@pytest.mark.django_db
def test_get_current_orders_requests_orders(itd_config, mock_CCAPI, itd_shipping_rules):
    calls = [
        call(
            order_type=1,
            number_of_days=models.ITDManifest.objects.DAYS_SINCE_DISPATCH,
            courier_rule_id=rule.rule_ID,
        )
        for rule in itd_shipping_rules
    ]
    models.ITDManifest.objects.get_current_orders()
    mock_CCAPI.get_orders_for_dispatch.assert_has_calls(calls, any_order=True)


@pytest.mark.django_db
def test_get_current_orders_returns_orders(
    itd_config_single_rule, mock_CCAPI, mock_orders
):
    assert models.ITDManifest.objects.get_current_orders() == mock_orders


@pytest.mark.django_db
def test_current_orders_filters_existing_orders(
    itd_config_single_rule, mock_CCAPI, mock_orders, itd_order_factory
):
    itd_order_factory.create(order_id=mock_orders[0].order_id)
    assert models.ITDManifest.objects.get_current_orders() == []


@pytest.mark.django_db
@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
@pytest.mark.parametrize(
    "status", [ITDManifest.CLOSED, ITDManifest.GENERATING, ITDManifest.ERROR]
)
def test_manifest_cannot_be_closed_unless_it_is_open(
    status, mock_CCAPI, itd_manifest_factory
):
    manifest = itd_manifest_factory.create(status=status)
    with pytest.raises(ValueError):
        manifest.close()
    assert manifest.status == status
    assert len(mock_CCAPI.mock_calls) == 0


@pytest.mark.django_db
@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
def test_close_manifest_creates_orders(
    itd_config_single_rule, country, mock_CCAPI, mock_orders, itd_manifest_factory
):
    manifest = itd_manifest_factory.create()
    manifest.close()
    for order in mock_orders:
        assert models.ITDOrder.objects.filter(
            order_id=order.order_id, manifest=manifest
        ).exists()


@pytest.mark.django_db
@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
def test_close_manifest_creates_products(
    itd_config_single_rule, country, mock_CCAPI, mock_orders, itd_manifest_factory
):
    manifest = itd_manifest_factory.create()
    manifest.close()
    for order in mock_orders:
        for product in order.products:
            assert models.ITDProduct.objects.filter(
                sku=product.sku, order__manifest=manifest
            ).exists()


@pytest.mark.django_db
@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
def test_close_manifest_creates_manifest_file(
    itd_config_single_rule, country, mock_CCAPI, mock_orders, itd_manifest_factory
):
    manifest = itd_manifest_factory.create()
    manifest.close()
    file_contents = manifest.manifest_file.read().decode("utf8")
    expected_contents = models._ITDManifestFile.create(mock_orders).getvalue()
    assert file_contents == expected_contents


@pytest.mark.django_db
@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
def test_close_manifest_marks_manifest_closed(
    itd_config_single_rule, country, mock_CCAPI, mock_orders, itd_manifest_factory
):
    manifest = itd_manifest_factory.create()
    manifest.close()
    assert manifest.status == manifest.CLOSED


@pytest.mark.django_db
@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
def test_close_manifest_error_marks_manifest_error(
    itd_config_single_rule,
    country,
    mock_get_orders_error,
    mock_orders,
    itd_manifest_factory,
):
    manifest = itd_manifest_factory.create()
    with pytest.raises(Exception):
        manifest.close()
    assert manifest.status == manifest.ERROR


@pytest.mark.django_db
@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
def test_close_manifest_does_not_create_orders_after_error(
    itd_config_single_rule,
    country,
    mock_get_orders_error,
    mock_orders,
    itd_manifest_factory,
):
    manifest = itd_manifest_factory.create()
    with pytest.raises(Exception):
        manifest.close()
    assert models.ITDOrder.objects.filter(manifest=manifest).exists() is False
