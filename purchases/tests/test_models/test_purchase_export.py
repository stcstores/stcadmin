import datetime as dt
from unittest import mock

import pytest
from django.conf import settings
from django.db.utils import IntegrityError
from django.utils import timezone

from purchases import models


@pytest.fixture
def purchase_settings(purchase_settings_factory):
    return purchase_settings_factory.create()


@pytest.fixture
def purchases(
    product_purchase_factory,
    shipping_purchase_factory,
    other_purchase_factory,
):
    return [
        product_purchase_factory.create(export=None),
        shipping_purchase_factory.create(export=None),
        other_purchase_factory.create(export=None),
    ]


@pytest.fixture
def purchase_export(purchase_export_factory):
    return purchase_export_factory.create(
        export_date=dt.date(day=1, month=2, year=2022)
    )


@pytest.fixture
def new_purchase_export():
    return models.PurchaseExport.objects.new_export()


@pytest.fixture
def purchases_on_export(product_purchase_factory, purchase_export):
    return product_purchase_factory.create_batch(3, export=purchase_export)


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
def test_purchase_export_has_date_created_attribute(purchase_export):
    assert isinstance(purchase_export.created_at, dt.datetime)


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
    purchases, product_purchase_factory
):
    models.PurchaseExport.objects.new_export()
    product_purchase_factory.create(export=None)
    with pytest.raises(IntegrityError):
        models.PurchaseExport.objects.new_export()


@pytest.mark.django_db
def test_str_method(purchase_export):
    assert str(purchase_export) == f"Purchase Report {purchase_export.export_date}"


@pytest.mark.django_db
def test_new_export_adds_unexported_purchases(product_purchase_factory):
    purchase = product_purchase_factory.create(export=None)
    export = models.PurchaseExport.objects.new_export()
    assert purchase in export.purchases.all()


@pytest.mark.django_db
def test_new_export_does_not_add_exported_purchases(
    purchase_export_factory, old_export, product_purchase_factory
):
    product_purchase_factory.create(export=None)
    purchase = product_purchase_factory.create(export=old_export)
    export = models.PurchaseExport.objects.new_export()
    assert purchase not in export.purchases.all()


@pytest.mark.django_db
def test_new_export_sets_export_date_yesterday():
    export = models.PurchaseExport.objects.new_export()
    assert export.export_date.date() == (timezone.now() - dt.timedelta(days=1)).date()


@pytest.mark.django_db
def test_get_report_filename(purchase_export):
    returned_value = purchase_export.get_report_filename()
    assert returned_value == "purchase_report_Feb_2022.csv"


@pytest.mark.django_db
@mock.patch("purchases.models.PurchaseExportReport.generate_report_text")
def test_generate_report(mock_generate_report_text, purchase_export):
    returned_value = purchase_export.generate_report()
    mock_generate_report_text.assert_called_once_with(purchase_export)
    assert returned_value == mock_generate_report_text.return_value


@pytest.mark.django_db
@mock.patch("purchases.models.EmailMessage")
def test_send_report_email(
    mock_email_message, purchases_on_export, purchase_settings, purchase_export
):
    purchase_export.generate_report = mock.Mock()
    purchase_export.send_report_email()
    mock_email_message.assert_called_once_with(
        subject="Staff Purchases Report Feb 2022",
        body="Please find this months staff purchase report attached.",
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[purchase_settings.send_report_to],
    )
    mock_email_message.return_value.attach.assert_called_once_with(
        purchase_export.get_report_filename(),
        purchase_export.generate_report.return_value.getvalue.return_value,
        "text/csv",
    )
    mock_email_message.return_value.send.assert_called_once_with()


@pytest.mark.django_db
@mock.patch("purchases.models.EmailMessage")
def test_send_empty_report_email(
    mock_email_message, purchase_settings, purchase_export
):
    purchase_export.generate_report = mock.Mock()
    purchase_export.send_report_email()
    mock_email_message.assert_called_once_with(
        subject="Staff Purchases Report Feb 2022",
        body="No staff purchases were made this month.",
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[purchase_settings.send_report_to],
    )
    mock_email_message.return_value.attach.assert_not_called
    mock_email_message.return_value.send.assert_called_once_with()
