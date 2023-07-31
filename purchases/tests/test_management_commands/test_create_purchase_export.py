from unittest import mock

import pytest
from django.core.management import call_command


@pytest.fixture
def command():
    return "create_purchase_export"


@pytest.fixture
def mock_purchase_export():
    with mock.patch(
        "purchases.management.commands.create_purchase_export.PurchaseExport"
    ) as mock_purchase_export:
        yield mock_purchase_export


@pytest.fixture
def mock_logger():
    with mock.patch(
        "purchases.management.commands.create_purchase_export.logger"
    ) as mock_logger:
        yield mock_logger


def test_calls_new_export(mock_purchase_export, command):
    call_command(command)
    mock_purchase_export.objects.new_export.assert_called_once_with()


def test_calls_send_report_email(mock_purchase_export, command):
    call_command(command)
    mock_purchase_export.objects.new_export.return_value.send_report_email.assert_called_once_with()


def test_logs_error_creating_export(mock_logger, mock_purchase_export, command):
    mock_purchase_export.objects.new_export.side_effect = Exception
    with pytest.raises(Exception):
        call_command(command)
    mock_logger.exception.assert_called_once_with(
        "Error creating staff purchase export."
    )


def test_logs_error_sending_email(mock_logger, mock_purchase_export, command):
    mock_purchase_export.objects.new_export.return_value.send_report_email.side_effect = (
        Exception
    )
    with pytest.raises(Exception):
        call_command(command)
    mock_logger.exception.assert_called_once_with(
        "Error sending staff purchase report email."
    )
