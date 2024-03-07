import datetime as dt
from unittest import mock

import pytest

from fba import models
from inventory.models import BaseProduct


@pytest.fixture
def profit_object(fba_profit_factory):
    return fba_profit_factory.create()


# Test Attributes


@pytest.mark.django_db
def test_full_clean(profit_object):
    assert profit_object.full_clean() is None


@pytest.mark.django_db
def test_has_gbp_currency_symbol_attribute(profit_object):
    assert profit_object.GBP_CURRENCY_SYMBOL == "£"


@pytest.mark.django_db
def test_has_import_record_attribute(profit_object):
    assert isinstance(profit_object.import_record, models.FBAProfitFile)


@pytest.mark.django_db
def test_has_product_attribute(profit_object):
    assert isinstance(profit_object.product, BaseProduct)


@pytest.mark.django_db
def test_has_region_attribute(profit_object):
    assert isinstance(profit_object.region, models.FBARegion)


@pytest.mark.django_db
def test_has_last_order_attribute(profit_object):
    assert isinstance(profit_object.last_order, models.FBAOrder)


@pytest.mark.django_db
def test_has_exchange_rate_attribute(profit_object):
    assert isinstance(profit_object.exchange_rate, float)


@pytest.mark.django_db
def test_has_channel_sku_attribute(profit_object):
    assert isinstance(profit_object.channel_sku, str)


@pytest.mark.django_db
def test_has_asin_attribute(profit_object):
    assert isinstance(profit_object.asin, str)


@pytest.mark.django_db
def test_has_listing_name_attribute(profit_object):
    assert isinstance(profit_object.listing_name, str)


@pytest.mark.django_db
def test_has_sale_price_attribute(profit_object):
    assert isinstance(profit_object.sale_price, int)


@pytest.mark.django_db
def test_has_referral_fee_attribute(profit_object):
    assert isinstance(profit_object.referral_fee, int)


@pytest.mark.django_db
def test_has_closing_fee_attribute(profit_object):
    assert isinstance(profit_object.closing_fee, int)


@pytest.mark.django_db
def test_has_handling_fee_attribute(profit_object):
    assert isinstance(profit_object.handling_fee, int)


@pytest.mark.django_db
def test_has_placement_feeattribute(profit_object):
    assert isinstance(profit_object.placement_fee, int)


@pytest.mark.django_db
def test_has_purchase_price_attribute(profit_object):
    assert isinstance(profit_object.purchase_price, int)


@pytest.mark.django_db
def test_has_shipping_price_attribute(profit_object):
    assert isinstance(profit_object.shipping_price, int)


@pytest.mark.django_db
def test_has_profit_attribute(profit_object):
    assert isinstance(profit_object.profit, int)


# Test Manager


@pytest.mark.django_db
def test_current_method(fba_profit_file_factory, fba_profit_factory):
    current_import = fba_profit_file_factory.create(import_date=dt.date(25, 3, 24))
    old_import = fba_profit_file_factory.create(import_date=dt.date(24, 3, 24))
    current_profit = fba_profit_factory.create(import_record=current_import)
    old_profit = fba_profit_factory.create(import_record=old_import)
    qs = models.FBAProfit.objects.current()
    assert qs.contains(current_profit)
    assert not qs.contains(old_profit)


# Test Methods


@pytest.mark.django_db
def test_str_method(profit_object):
    expected = (
        f"{profit_object.product.sku} - {profit_object.import_record.import_date}"
    )
    assert str(profit_object) == expected


@pytest.mark.parametrize(
    "symbol,value,expected",
    (
        ("£", 520, " £5.20"),
        ("£", -520, "-£5.20"),
        ("£", 0, " £0.00"),
        ("$", 520, " $5.20"),
        ("$", -520, "-$5.20"),
        ("£", 94857, " £948.57"),
    ),
)
def test_format_price_method(symbol, value, expected):
    assert models.FBAProfit._format_price(symbol, value) == expected


def test_local_price_method():
    profit = mock.Mock()
    profit.exchange_rate = 0.5
    value = 1
    value = models.FBAProfit._local_price(profit, value)
    assert value == profit._format_price.return_value
    profit._format_price.assert_called_once_with(profit.region.currency.symbol, 2.0)


@pytest.fixture
def mock_format_price():
    with mock.patch("fba.models.profit.FBAProfit._format_price") as m:
        yield m


@pytest.fixture
def mock_gbp_price():
    with mock.patch("fba.models.profit.FBAProfit._gbp_price") as m:
        yield m


@pytest.fixture
def mock_local_price():
    with mock.patch("fba.models.profit.FBAProfit._local_price") as m:
        yield m


@pytest.mark.django_db
def test_gbp_price(mock_format_price, profit_object):
    value = 520
    assert profit_object._gbp_price(value) == mock_format_price.return_value
    mock_format_price.assert_called_once_with(profit_object.GBP_CURRENCY_SYMBOL, value)


@pytest.mark.django_db
def test_sale_price_gbp(mock_gbp_price, profit_object):
    assert profit_object.sale_price_gbp() == mock_gbp_price.return_value
    mock_gbp_price.assert_called_once_with(profit_object.sale_price)


@pytest.mark.django_db
def test_sale_price_local(mock_local_price, profit_object):
    assert profit_object.sale_price_local() == mock_local_price.return_value
    mock_local_price.assert_called_once_with(profit_object.sale_price)


@pytest.mark.django_db
def test_referral_fee_gbp(mock_gbp_price, profit_object):
    assert profit_object.referral_fee_gbp() == mock_gbp_price.return_value
    mock_gbp_price.assert_called_once_with(profit_object.referral_fee)


@pytest.mark.django_db
def test_referral_fee_local(mock_local_price, profit_object):
    assert profit_object.referral_fee_local() == mock_local_price.return_value
    mock_local_price.assert_called_once_with(profit_object.referral_fee)


@pytest.mark.django_db
def test_closing_fee_gbp(mock_gbp_price, profit_object):
    assert profit_object.closing_fee_gbp() == mock_gbp_price.return_value
    mock_gbp_price.assert_called_once_with(profit_object.closing_fee)


@pytest.mark.django_db
def test_closing_fee_local(mock_local_price, profit_object):
    assert profit_object.closing_fee_local() == mock_local_price.return_value
    mock_local_price.assert_called_once_with(profit_object.closing_fee)


@pytest.mark.django_db
def test_handling_fee_gbp(mock_gbp_price, profit_object):
    assert profit_object.handling_fee_gbp() == mock_gbp_price.return_value
    mock_gbp_price.assert_called_once_with(profit_object.handling_fee)


@pytest.mark.django_db
def test_handling_fee_local(mock_local_price, profit_object):
    assert profit_object.handling_fee_local() == mock_local_price.return_value
    mock_local_price.assert_called_once_with(profit_object.handling_fee)


@pytest.mark.django_db
def test_placement_fee_gbp(mock_gbp_price, profit_object):
    assert profit_object.placement_fee_gbp() == mock_gbp_price.return_value
    mock_gbp_price.assert_called_once_with(profit_object.placement_fee)


@pytest.mark.django_db
def test_placement_fee_local(mock_local_price, profit_object):
    assert profit_object.placement_fee_local() == mock_local_price.return_value
    mock_local_price.assert_called_once_with(profit_object.placement_fee)


@pytest.mark.django_db
def test_purchase_price_gbp(mock_gbp_price, profit_object):
    assert profit_object.purchase_price_gbp() == mock_gbp_price.return_value
    mock_gbp_price.assert_called_once_with(profit_object.purchase_price)


@pytest.mark.django_db
def test_purchase_price_local(mock_local_price, profit_object):
    assert profit_object.purchase_price_local() == mock_local_price.return_value
    mock_local_price.assert_called_once_with(profit_object.purchase_price)


@pytest.mark.django_db
def test_shipping_price_gbp(mock_gbp_price, profit_object):
    assert profit_object.shipping_price_gbp() == mock_gbp_price.return_value
    mock_gbp_price.assert_called_once_with(profit_object.shipping_price)


@pytest.mark.django_db
def test_shipping_price_local(mock_local_price, profit_object):
    assert profit_object.shipping_price_local() == mock_local_price.return_value
    mock_local_price.assert_called_once_with(profit_object.shipping_price)


@pytest.mark.django_db
def test_profit_gbp(mock_gbp_price, profit_object):
    assert profit_object.profit_gbp() == mock_gbp_price.return_value
    mock_gbp_price.assert_called_once_with(profit_object.profit)


@pytest.mark.django_db
def test_profit_local(mock_local_price, profit_object):
    assert profit_object.profit_local() == mock_local_price.return_value
    mock_local_price.assert_called_once_with(profit_object.profit)
