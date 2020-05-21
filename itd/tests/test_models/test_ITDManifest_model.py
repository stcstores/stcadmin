import tempfile
from datetime import datetime
from pathlib import Path
from unittest.mock import call, patch

import pytest
from django.core.files.base import ContentFile
from django.test import override_settings
from django.utils import timezone

from itd import models


@pytest.fixture
def new_manifest():
    manifest = models.ITDManifest()
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


@pytest.fixture
def mock_clear_manifest_files_task():
    with patch("itd.models.clear_manifest_files") as mock_clear_manifest_files_task:
        yield mock_clear_manifest_files_task


@pytest.fixture
def mock_regenerate_manifest_task():
    with patch("itd.models.regenerate_manifest") as mock_regenerate_manifest_task:
        yield mock_regenerate_manifest_task


@pytest.mark.django_db
def test_default_created_at_attribute(mock_now, new_manifest):
    assert new_manifest.created_at == mock_now


@pytest.mark.django_db
def test_last_generated_at_attribute(mock_now, new_manifest):
    assert new_manifest.last_generated_at is None


@pytest.mark.django_db
def test_status_attribute(new_manifest):
    assert new_manifest.status == models.ITDManifest.OPEN


@pytest.mark.django_db
def test_manifest_file_attribute(new_manifest):
    assert bool(new_manifest.manifest_file) is False


@pytest.mark.django_db
def test_manifest_ordering(itd_manifest_factory):
    dates = [
        timezone.make_aware(datetime(*date))
        for date in ((2020, 5, 13), (2019, 12, 15), (2020, 1, 16))
    ]
    for date in dates:
        itd_manifest_factory.create(created_at=date)
    manifests = models.ITDManifest.objects.all()
    assert list(manifests) == sorted(
        list(manifests), key=lambda x: x.created_at, reverse=True
    )


@pytest.mark.django_db
def test_create_manifest_closes_manifest():
    with patch("itd.models.close_manifest") as mock_close_manifest_task:
        manifest = models.ITDManifest.objects.create_manifest()
    mock_close_manifest_task.delay.assert_called_once_with(manifest.id)


@pytest.mark.django_db
def test_get_current_orders_requests_orders(itd_config, mock_CCAPI, itd_shipping_rules):
    calls = [
        call(order_type=0, number_of_days=0, courier_rule_id=rule.rule_ID,)
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
    "status",
    [
        models.ITDManifest.CLOSED,
        models.ITDManifest.GENERATING,
        models.ITDManifest.ERROR,
        models.ITDManifest.NO_ORDERS,
    ],
)
def test_manifest_cannot_be_closed_unless_it_is_open(
    mock_now, status, mock_CCAPI, itd_manifest_factory
):
    manifest = itd_manifest_factory.create(status=status)
    with pytest.raises(ValueError):
        manifest.close()
    assert manifest.status == status
    assert len(mock_CCAPI.mock_calls) == 0


@pytest.mark.django_db
@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
def test_close_creates_orders(
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
def test_close_schedules_file_deletion(
    mock_now,
    mock_clear_manifest_files_task,
    itd_config_single_rule,
    country,
    mock_CCAPI,
    mock_orders,
    itd_manifest_factory,
):
    manifest = itd_manifest_factory.create()
    manifest.close()
    mock_clear_manifest_files_task.apply_async.assert_called_once_with(
        args=[manifest.id], eta=mock_now + models.ITDManifest.PERSIST_FILES
    )


@pytest.mark.django_db
@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
def test_close_creates_products(
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
def test_close_creates_manifest_file(
    mock_clear_manifest_files_task,
    itd_config_single_rule,
    country,
    mock_CCAPI,
    mock_orders,
    itd_manifest_factory,
):
    manifest = itd_manifest_factory.create()
    manifest.close()
    file_contents = manifest.manifest_file.read().decode("utf8")
    expected_contents = models._ITDManifestFile.create(mock_orders).getvalue()
    assert file_contents == expected_contents


@pytest.mark.django_db
@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
def test_close_marks_manifest_closed(
    mock_clear_manifest_files_task,
    itd_config_single_rule,
    country,
    mock_CCAPI,
    mock_orders,
    itd_manifest_factory,
):
    manifest = itd_manifest_factory.create()
    manifest.close()
    assert manifest.status == manifest.CLOSED


@pytest.mark.django_db
@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
def test_close_error_marks_manifest_error(
    mock_clear_manifest_files_task,
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
def test_close_does_not_create_orders_after_error(
    mock_clear_manifest_files_task,
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


@pytest.mark.django_db
@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
def test_no_new_orders(
    mock_clear_manifest_files_task,
    itd_config_single_rule,
    country,
    mock_CCAPI,
    itd_manifest_factory,
):
    manifest = itd_manifest_factory.create()
    manifest.close()
    manifest.refresh_from_db()
    assert manifest.status == manifest.NO_ORDERS
    assert bool(manifest.manifest_file) is False


@pytest.mark.django_db
@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
def test_clear_files(itd_manifest_factory):
    manifest = itd_manifest_factory.create()
    manifest.manifest_file.save("test_file.csv", ContentFile("test_text"))
    file_path = manifest.manifest_file.path
    manifest.clear_files()
    assert Path(file_path).exists() is False
    assert bool(manifest.manifest_file) is False


@pytest.mark.django_db
@patch("itd.models.ITDManifest.close")
def test_close_manifest(mock_close, itd_manifest_factory):
    manifest = itd_manifest_factory.create()
    models.ITDManifest.objects.close_manifest(manifest.id)
    mock_close.assert_called_once()


@pytest.mark.django_db
def test_ready_to_create_returns_true_if_no_manifest_exists():
    assert models.ITDManifest.objects.ready_to_create() is True


@pytest.mark.django_db
def test_ready_to_create_returns_false_if_a_manifest_is_open(itd_manifest_factory):
    itd_manifest_factory.create(status=models.ITDManifest.OPEN)
    assert models.ITDManifest.objects.ready_to_create() is False


@pytest.mark.django_db
def test_ready_to_create_returns_false_if_a_manifest_is_generating(
    itd_manifest_factory,
):
    itd_manifest_factory.create(status=models.ITDManifest.GENERATING)
    assert models.ITDManifest.objects.ready_to_create() is False


@pytest.fixture
@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
def regenerated_manifest(
    mock_clear_manifest_files_task,
    mock_CCAPI,
    country,
    mock_orders,
    itd_manifest_factory,
    itd_order_factory,
):
    manifest = itd_manifest_factory.create(status=models.ITDManifest.CLOSED)
    for _ in range(5):
        itd_order_factory.create(manifest=manifest)
    manifest.regenerate()
    manifest.refresh_from_db()
    return manifest


@pytest.mark.django_db
def test_regenerate_requests_orders(mock_CCAPI, regenerated_manifest):
    calls = [
        call(search_term=order.order_id)
        for order in regenerated_manifest.itdorder_set.all()
    ]
    mock_CCAPI.get_orders_for_dispatch.assert_has_calls(calls)


@pytest.mark.django_db
def test_regenerate_creates_file(regenerated_manifest):
    assert bool(regenerated_manifest.manifest_file) is True


@pytest.mark.django_db
def test_regenerate_sets_manifest_closed(regenerated_manifest):
    assert regenerated_manifest.status == regenerated_manifest.CLOSED


@pytest.mark.django_db
def test_regenerate_calls_clear_files(
    mock_now, mock_clear_manifest_files_task, regenerated_manifest
):
    mock_clear_manifest_files_task.apply_async.assert_called_once_with(
        args=[regenerated_manifest.id], eta=mock_now + models.ITDManifest.PERSIST_FILES
    )


@pytest.mark.django_db
def test_regenerate_sets_last_generated_at(mock_now, regenerated_manifest):
    assert regenerated_manifest.last_generated_at == mock_now


@pytest.mark.django_db
@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
def test_regenerate_error(
    mock_get_orders_error,
    mock_clear_manifest_files_task,
    itd_manifest_factory,
    itd_order_factory,
):
    manifest = itd_manifest_factory.create(status=models.ITDManifest.CLOSED)
    itd_order_factory.create(manifest=manifest)
    with pytest.raises(Exception):
        manifest.regenerate()
    manifest.refresh_from_db()
    assert manifest.status == manifest.ERROR


@pytest.mark.django_db
@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
@pytest.mark.parametrize(
    "status",
    (
        models.ITDManifest.OPEN,
        models.ITDManifest.GENERATING,
        models.ITDManifest.ERROR,
        models.ITDManifest.NO_ORDERS,
    ),
)
def test_regenerate_only_allowed_on_closed_manifests(itd_manifest_factory, status):
    manifest = itd_manifest_factory.create(status=status)
    with pytest.raises(ValueError):
        manifest.regenerate()


@pytest.mark.django_db
@patch("itd.models.ITDManifest.regenerate")
def test_regenerate_manifest(mock_regenerate, itd_manifest_factory):
    manifest = itd_manifest_factory.create(status=models.ITDManifest.CLOSED)
    models.ITDManifest.objects.regenerate_manifest(manifest.id)
    mock_regenerate.assert_called_once()


@pytest.mark.django_db
def test_regenerate_async(mock_regenerate_manifest_task, itd_manifest_factory):
    manifest = itd_manifest_factory.create(status=models.ITDManifest.CLOSED)
    manifest.regenerate_async()
    mock_regenerate_manifest_task.delay.assert_called_once_with(manifest.id)
