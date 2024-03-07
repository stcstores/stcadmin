import datetime as dt
from unittest import mock

import pytest
from django.core.exceptions import ObjectDoesNotExist

from fba import models


@pytest.fixture
def profit_file(fba_profit_file_factory):
    return fba_profit_file_factory.create()


@pytest.mark.django_db
def test_full_clean(profit_file):
    assert profit_file.full_clean() is None


# Test Attributes


@pytest.mark.django_db
def test_has_import_date_attribute(profit_file):
    assert isinstance(profit_file.import_date, dt.datetime)


# Test Manager


@pytest.fixture
def mock_fba_profit_calculation():
    with mock.patch("fba.models.profit._FBAProfitCalculation") as m:
        yield m


@pytest.fixture
def mock_fee_estimate_file_uk():
    with mock.patch("fba.models.profit.FeeEstimateFileUK") as m:
        m.return_value.fees = [mock.Mock() for _ in range(3)]
        yield m


@pytest.fixture
def mock_fee_estimate_file_us():
    with mock.patch("fba.models.profit.FeeEstimateFileUS") as m:
        m.return_value.fees = [mock.Mock() for _ in range(3)]
        yield m


@pytest.fixture
def mock_create_method():
    with mock.patch("fba.models.profit.FBAProfitFile.FBAProfitFileManager.create") as m:
        yield m


@pytest.fixture
def mock_create_from_fee_method():
    with mock.patch(
        "fba.models.profit.FBAProfitFile.FBAProfitFileManager.create_from_fee"
    ) as m:
        yield m


@pytest.fixture
def mock_bulk_create_method():
    with mock.patch("fba.models.profit.FBAProfit.objects.bulk_create") as m:
        yield m


@pytest.mark.django_db
def test_update_from_exports_method(
    mock_fee_estimate_file_uk,
    mock_fee_estimate_file_us,
    mock_create_method,
    mock_create_from_fee_method,
    mock_bulk_create_method,
):
    fees = (
        mock_fee_estimate_file_uk.return_value.fees
        + mock_fee_estimate_file_us.return_value.fees
    )
    models.FBAProfitFile.objects.update_from_exports()
    mock_create_method.assert_called_once_with()
    mock_create_from_fee_method.assert_has_calls(
        (mock.call(mock_create_method.return_value, fee) for fee in fees),
        any_order=True,
    )
    mock_bulk_create_method.assert_called_once_with(
        [mock_create_from_fee_method.return_value for _ in range(len(fees))]
    )


@pytest.mark.django_db
def test_update_from_exports_method_ignores_invalid_fees(
    mock_fee_estimate_file_uk,
    mock_fee_estimate_file_us,
    mock_create_method,
    mock_create_from_fee_method,
    mock_bulk_create_method,
):
    mock_fee_estimate_file_uk.return_value.fees = [mock.Mock(), mock.Mock()]
    mock_fee_estimate_file_us.return_value.fees = []
    mock_obj = mock.Mock()
    mock_create_from_fee_method.side_effect = [mock_obj, None]
    models.FBAProfitFile.objects.update_from_exports()
    mock_bulk_create_method.assert_called_once_with([mock_obj])


def test_create_from_fee_method(mock_fba_profit_calculation):
    import_record = mock.Mock()
    fee = mock.Mock()
    value = models.FBAProfitFile.objects.create_from_fee(
        import_record=import_record, fee=fee
    )
    mock_fba_profit_calculation.assert_called_once_with(fee)
    mock_fba_profit_calculation.return_value.to_object.assert_called_once_with(
        import_record
    )
    assert value == mock_fba_profit_calculation.return_value.to_object.return_value


def test_create_from_fee_method_with_object_not_found(mock_fba_profit_calculation):
    mock_fba_profit_calculation.return_value.to_object.side_effect = ObjectDoesNotExist
    import_record = mock.Mock()
    fee = mock.Mock()
    value = models.FBAProfitFile.objects.create_from_fee(
        import_record=import_record, fee=fee
    )
    assert value is None


# Test Methods


@pytest.mark.django_db
def test_str_method(profit_file):
    assert str(profit_file) == f"FBA Profit File {profit_file.import_date}"
