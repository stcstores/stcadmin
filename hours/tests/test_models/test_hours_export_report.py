import datetime as dt
from unittest import mock

import pytest

from hours.models import HoursExportReport


@pytest.fixture
def report_generator():
    return HoursExportReport(10, 2024)


def test_month_length():
    assert HoursExportReport(10, 2024).month_length == 31


def test_header():
    assert HoursExportReport(10, 2024).header == [
        "October 2024",
        1,
        2,
        3,
        4,
        5,
        6,
        7,
        8,
        9,
        10,
        11,
        12,
        13,
        14,
        15,
        16,
        17,
        18,
        19,
        20,
        21,
        22,
        23,
        24,
        25,
        26,
        27,
        28,
        29,
        30,
        31,
    ]


@mock.patch("hours.models.ClockTime")
def test_get_day(mock_clock_time, report_generator):
    staff_member = mock.Mock()
    date = dt.date(2024, 10, 10)
    mock_clock_time.objects.filter.return_value = [
        mock.Mock(timestamp=dt.datetime(2024, 10, 10, 10, 0)),
        mock.Mock(timestamp=dt.datetime(2024, 10, 10, 13, 0)),
        mock.Mock(timestamp=dt.datetime(2024, 10, 10, 13, 30)),
        mock.Mock(timestamp=dt.datetime(2024, 10, 10, 16, 0)),
    ]
    return_value = report_generator._get_day(staff_member, date)
    mock_clock_time.objects.filter.assert_called_once_with(
        user=staff_member, timestamp__date=date
    )
    assert return_value == "10:00\n13:00\n13:30\n16:00"


@mock.patch("hours.models.HoursExportReport._get_day")
def test_get_row(mock_get_day, report_generator):
    staff_member = mock.Mock(full_name=mock.Mock(return_value="Jeremy Glog"))
    return_value = report_generator._get_row(staff_member)
    mock_get_day.assert_has_calls(
        [mock.call(staff_member, dt.date(2024, 10, day)) for day in range(1, 32)]
    )
    expected = ["Jeremy Glog"] + ([mock_get_day.return_value] * 31)
    assert return_value == expected


@mock.patch("hours.models.Staff")
@mock.patch("hours.models.HoursExportReport._get_row")
def test_get_report_data(mock_get_row, mock_staff_model, report_generator):
    staff = [mock.Mock(), mock.Mock()]
    mock_staff_model.objects.filter.return_value = staff
    return_value = report_generator._get_report_data()
    mock_staff_model.objects.filter.assert_called_once_with(can_clock_in=True)
    mock_get_row.assert_has_calls([mock.call(staff_member) for staff_member in staff])
    expected = [
        report_generator.header,
        mock_get_row.return_value,
        report_generator.header,
        mock_get_row.return_value,
    ]
    assert return_value == expected


@mock.patch("hours.models.StringIO")
@mock.patch("hours.models.csv")
@mock.patch("hours.models.HoursExportReport._get_report_data")
def test_generate_report_text(
    mock_get_report_data, mock_csv, mock_string_io, report_generator
):
    return_value = report_generator.generate_report_text()
    mock_get_report_data.assert_called_once()
    mock_csv.writer.assert_called_once_with(mock_string_io.return_value)
    mock_csv.writer.return_value.writerows.assert_called_once_with(
        mock_get_report_data.return_value
    )
    assert return_value == mock_string_io.return_value
