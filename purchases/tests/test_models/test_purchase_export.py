import datetime as dt
from unittest import mock

import pytest
from django.db.utils import IntegrityError

from purchases import models


@pytest.fixture
def purchases(purchase_factory):
    return purchase_factory.create_batch(3, export=None)


@pytest.fixture
def purchase_export(purchase_export_factory):
    return purchase_export_factory.create()


@pytest.fixture
def new_purchase_export():
    return models.PurchaseExport.objects.new_export()


@pytest.fixture
def old_export(purchase_export_factory):
    old_export = purchase_export_factory.create()
    old_export.export_date = dt.date(2022, 11, 15)
    old_export.save()
    return old_export


@pytest.mark.django_db
def test_purchase_export_has_export_date_attribute(purchase_export):
    assert isinstance(purchase_export.export_date, dt.date)


@pytest.mark.django_db
def test_new_export_creates_empty_export():
    export = models.PurchaseExport.objects.new_export()
    assert export.purchases.count() == 0


@pytest.mark.django_db
def test_purchase_export_has_report_sent_attribute(purchase_export):
    assert isinstance(purchase_export.report_sent, bool)


@pytest.mark.django_db
def test_purchase_export_report_sent_defaults_to_false(purchases, new_purchase_export):
    assert new_purchase_export.report_sent is False


@pytest.mark.django_db
def test_purchase_exports_cannot_be_created_with_matching_dates(
    purchases, purchase_factory
):
    models.PurchaseExport.objects.new_export()
    purchase_factory.create(export=None)
    with pytest.raises(IntegrityError):
        models.PurchaseExport.objects.new_export()


@pytest.mark.django_db
def test_new_export_adds_unexported_purchases(purchase_factory):
    purchase = purchase_factory.create(export=None)
    export = models.PurchaseExport.objects.new_export()
    assert purchase in export.purchases.all()


@pytest.mark.django_db
def test_new_export_does_not_add_exported_purchases(
    purchase_export_factory, old_export, purchase_factory
):
    purchase_factory.create(export=None)
    purchase = purchase_factory.create(export=old_export)
    export = models.PurchaseExport.objects.new_export()
    assert purchase not in export.purchases.all()


@pytest.mark.django_db
@mock.patch("purchases.models.PurchaseExportReport.generate_report_text")
def test_generate_report(mock_generate_report_text, purchase_export):
    returned_value = purchase_export.generate_report()
    mock_generate_report_text.assert_called_once_with(purchase_export)
    assert returned_value == mock_generate_report_text.return_value
