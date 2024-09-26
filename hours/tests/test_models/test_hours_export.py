import datetime as dt
from unittest import mock

import pytest
from django.conf import settings
from django.db.utils import IntegrityError
from django.utils import timezone

from hours import models


@pytest.fixture
def hours_settings(hours_settings_factory):
    return hours_settings_factory.create()


@pytest.fixture
def hours():
    return []


@pytest.fixture
def hours_export(hours_export_factory):
    return hours_export_factory.create(export_date=dt.date(day=1, month=2, year=2022))


@pytest.fixture
def new_hours_export():
    return models.HoursExport.objects.new_export()


@pytest.fixture
def hours_on_export(clock_time_factory, hours_export):
    return clock_time_factory.create_batch(3, export=hours_export)


@pytest.fixture
def old_export(hours_export_factory):
    old_export = hours_export_factory.create()
    old_export.export_date = dt.date(2022, 11, 15)
    old_export.save()
    return old_export


@pytest.mark.django_db
def test_hours_export_has_export_date_attribute(hours_export):
    assert isinstance(hours_export.export_date, dt.date)


@pytest.mark.django_db
def test_hours_export_has_date_created_attribute(hours_export):
    assert isinstance(hours_export.created_at, dt.datetime)


@pytest.mark.django_db
def test_new_export_creates_empty_export():
    export = models.HoursExport.objects.new_export()
    assert export.id is not None


@pytest.mark.django_db
def test_hours_export_has_report_sent_attribute(hours_export):
    assert isinstance(hours_export.report_sent, bool)


@pytest.mark.django_db
def test_hours_export_report_sent_defaults_to_false(hours, new_hours_export):
    assert new_hours_export.report_sent is False


@pytest.mark.django_db
def test_hours_exports_cannot_be_created_with_matching_dates():
    models.HoursExport.objects.new_export()
    with pytest.raises(IntegrityError):
        models.HoursExport.objects.new_export()


@pytest.mark.django_db
def test_str_method(hours_export):
    expected = f"Hours Report {hours_export.export_date.strftime('%b %Y')}"
    assert str(hours_export) == expected


@pytest.mark.django_db
def test_new_export_sets_export_date_yesterday():
    export = models.HoursExport.objects.new_export()
    assert export.export_date.date() == (timezone.now() - dt.timedelta(days=1)).date()


@pytest.mark.django_db
def test_get_report_filename(hours_export):
    returned_value = hours_export.get_report_filename()
    assert returned_value == "staff_hours_Feb_2022.csv"


@pytest.mark.django_db
@mock.patch("hours.models.HoursExportReport.generate_report_text")
def test_generate_report(mock_generate_report_text, hours_export):
    returned_value = hours_export.generate_report()
    mock_generate_report_text.assert_called_once_with(2, 2022)
    assert returned_value == mock_generate_report_text.return_value


@pytest.mark.django_db
@mock.patch("hours.models.EmailMessage")
def test_send_report_email(mock_email_message, hours_settings, hours_export):
    hours_export.generate_report = mock.Mock()
    hours_export.send_report_email()
    mock_email_message.assert_called_once_with(
        subject="Staff Hours Report Feb 2022",
        body="Please find this months staff hours report attached.",
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[hours_settings.send_report_to],
    )
    mock_email_message.return_value.attach.assert_called_once_with(
        hours_export.get_report_filename(),
        hours_export.generate_report.return_value.getvalue.return_value,
        "text/csv",
    )
    mock_email_message.return_value.send.assert_called_once_with()


@pytest.mark.django_db
@mock.patch("hours.models.EmailMessage")
def test_send_report_email_when_report_sent_is_true(mock_email_message, hours_export):
    hours_export.report_sent = True
    hours_export.generate_report = mock.Mock()
    with pytest.raises(Exception, match=f"{hours_export} Already Sent."):
        hours_export.send_report_email()
