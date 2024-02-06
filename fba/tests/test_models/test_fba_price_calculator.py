from unittest import mock

import pytest

from fba.models.price_calculator import FBAPriceCalculator
from shipping.models import Region


def test_has_CHANNEL_FEE_attribute():
    assert FBAPriceCalculator.CHANNEL_FEE == 0.15


@pytest.fixture
def selling_price():
    return 55.20


@pytest.fixture
def exchange_rate():
    return 0.806


@pytest.fixture
def currency_symbol():
    return "$"


@pytest.fixture
def region(exchange_rate, currency_symbol):
    region = mock.Mock()
    region.country.currency.symbol = currency_symbol
    region.country.currency.exchange_rate.return_value = exchange_rate
    return region


@pytest.fixture
def purchase_price():
    return 12


@pytest.fixture
def fba_fee():
    return 4.80


@pytest.fixture
def product_weight():
    return 220


@pytest.fixture
def quantity():
    return 27


@pytest.fixture
def stock_level():
    return 27


@pytest.fixture
def calculator_kwargs(
    selling_price,
    region,
    purchase_price,
    fba_fee,
    product_weight,
    quantity,
    stock_level,
):
    return {
        "selling_price": selling_price,
        "region": region,
        "purchase_price": purchase_price,
        "fba_fee": fba_fee,
        "product_weight": product_weight,
        "stock_level": stock_level,
        "zero_rated": False,
        "quantity": quantity,
    }


@pytest.fixture
def calculator(calculator_kwargs):
    return FBAPriceCalculator(**calculator_kwargs)


def test_has_selling_price_attribute(calculator, selling_price):
    assert calculator.selling_price == selling_price


def test_has_region_attribute(calculator, region):
    assert calculator.region == region


def test_has_purchase_price_attribute(calculator, purchase_price):
    assert calculator.purchase_price == purchase_price


def test_has_fba_fee_attribute(calculator, fba_fee):
    assert calculator.fba_fee == fba_fee


def test_has_product_weight_attribute(calculator, product_weight):
    assert calculator.product_weight == product_weight


def test_has_quantity_attribute(calculator, quantity):
    assert calculator.quantity == quantity


def test_has_stock_level_attribute(calculator, stock_level):
    assert calculator.stock_level == stock_level


def test_has_zero_rated_attribute(calculator):
    assert calculator.zero_rated is False


@pytest.fixture
def max_quantity():
    return 50


@pytest.fixture
def max_quantity_no_stock():
    return 100


@pytest.fixture
def postage_gbp():
    return 2.273


@pytest.fixture
def vat():
    return 9.222


@pytest.fixture
def profit():
    return 3.352


@pytest.fixture
def calculated_calculator(
    calculator, vat, max_quantity, max_quantity_no_stock, postage_gbp, profit
):
    calculator.get_max_quantity = mock.Mock(
        return_value=(max_quantity, max_quantity_no_stock)
    )
    calculator.get_postage_to_fba = mock.Mock(return_value=postage_gbp)
    calculator.get_vat = mock.Mock(return_value=vat)
    calculator.calculate_profit = mock.Mock(return_value=profit)
    calculator.calculate()
    return calculator


def test_has_exchange_rate_attribute(calculated_calculator, exchange_rate):
    assert calculated_calculator.exchange_rate == float(exchange_rate)


def test_has_max_quantity_attribute(
    calculated_calculator, max_quantity, region, product_weight, stock_level
):
    calculated_calculator.get_max_quantity.assert_called_once_with(
        region=region, product_weight=product_weight, stock_level=stock_level
    )
    assert calculated_calculator.max_quantity == max_quantity


def test_has_max_quantity_no_stock_attribute(
    calculated_calculator, max_quantity_no_stock, region, product_weight, stock_level
):
    calculated_calculator.get_max_quantity.assert_called_once_with(
        region=region, product_weight=product_weight, stock_level=stock_level
    )
    assert calculated_calculator.max_quantity_no_stock == max_quantity_no_stock


def test_has_postage_gbp_attribute(
    calculated_calculator, postage_gbp, region, product_weight, quantity
):
    calculated_calculator.get_postage_to_fba.assert_called_once_with(
        region=region, product_weight=product_weight, quantity=quantity
    )
    assert calculated_calculator.postage_gbp == postage_gbp


def test_has_postage_local_attribute(calculated_calculator, postage_gbp, exchange_rate):
    assert calculated_calculator.postage_local == postage_gbp / exchange_rate


def test_has_vat_attribute(calculated_calculator, vat, region, selling_price):
    calculated_calculator.get_vat.assert_called_once_with(
        region=region, selling_price=selling_price, zero_rated=False
    )
    assert calculated_calculator.vat == vat


def test_has_channel_fee_attribute(calculated_calculator, selling_price):
    assert (
        calculated_calculator.channel_fee
        == selling_price * calculated_calculator.CHANNEL_FEE
    )


def test_has_purchase_price_local_attribute(
    calculated_calculator, purchase_price, exchange_rate
):
    assert calculated_calculator.purchase_price_local == purchase_price / exchange_rate


def test_has_postage_per_item_gbp_attribute(
    calculated_calculator, postage_gbp, quantity
):
    assert calculated_calculator.postage_per_item_gbp == postage_gbp / quantity


def test_has_postage_per_item_local_attribute(
    calculated_calculator, postage_gbp, quantity, exchange_rate
):
    assert (
        calculated_calculator.postage_per_item_local
        == (postage_gbp / quantity) / exchange_rate
    )


def test_has_profit_attribute(
    calculated_calculator,
    profit,
    selling_price,
    postage_gbp,
    quantity,
    exchange_rate,
    vat,
    purchase_price,
    fba_fee,
):
    calculated_calculator.calculate_profit.assert_called_once_with(
        selling_price=selling_price,
        postage_per_item_local=(postage_gbp / quantity) / exchange_rate,
        channel_fee=selling_price * calculated_calculator.CHANNEL_FEE,
        vat=vat,
        purchase_price_local=purchase_price / exchange_rate,
        fba_fee=fba_fee,
    )
    assert calculated_calculator.profit == profit


def test_has_profit_gbp_attribute(calculated_calculator, profit, exchange_rate):
    assert calculated_calculator.profit_gbp == profit * exchange_rate


def test_percentage(calculated_calculator, profit, selling_price):
    assert calculated_calculator.percentage == (profit / selling_price) * 100


def test_to_dict_method(calculated_calculator):
    assert calculated_calculator.to_dict() == {
        "channel_fee": round(calculated_calculator.channel_fee, 2),
        "currency_symbol": calculated_calculator.region.country.currency.symbol,
        "vat": round(calculated_calculator.vat, 2),
        "postage_to_fba": round(calculated_calculator.postage_gbp, 2),
        "postage_per_item": round(calculated_calculator.postage_per_item_gbp, 2),
        "profit": round(calculated_calculator.profit_gbp, 2),
        "percentage": round(calculated_calculator.percentage, 2),
        "purchase_price": round(calculated_calculator.purchase_price_local, 2),
        "max_quantity": calculated_calculator.max_quantity,
        "max_quantity_no_stock": calculated_calculator.max_quantity_no_stock,
    }


@pytest.mark.parametrize(
    "vat_is_required,zero_rated,selling_price,expected",
    (
        (Region.VAT_NEVER, True, 6.00, 0.0),
        (Region.VAT_NEVER, False, 6.00, 0.0),
        (Region.VAT_ALWAYS, True, 6.00, 0.0),
        (Region.VAT_ALWAYS, False, 6.00, 1.0),
        (Region.VAT_VARIABLE, True, 6.00, 0.0),
        (Region.VAT_VARIABLE, False, 6.00, 1.0),
    ),
)
def test_get_vat(vat_is_required, zero_rated, selling_price, expected):
    region = mock.Mock()
    region.country.VAT_NEVER = Region.VAT_NEVER
    region.country.vat_is_required.return_value = vat_is_required
    value = FBAPriceCalculator.get_vat(
        region=region, zero_rated=zero_rated, selling_price=selling_price
    )
    assert value == expected


def test_get_postage_to_fba():
    region = mock.Mock()
    region.calculate_shipping.return_value = 1500
    product_weight = 10
    quantity = 5
    value = FBAPriceCalculator.get_postage_to_fba(
        region=region, product_weight=product_weight, quantity=quantity
    )
    region.calculate_shipping.assert_called_once_with(50)
    assert value == 15.00


def test_calculate_profit():
    selling_price = 35.0
    postage_per_item_local = 5.0
    channel_fee = 5.0
    vat = 5.0
    purchase_price_local = 5.0
    fba_fee = 5.0
    assert (
        FBAPriceCalculator.calculate_profit(
            selling_price=selling_price,
            postage_per_item_local=postage_per_item_local,
            channel_fee=channel_fee,
            vat=vat,
            purchase_price_local=purchase_price_local,
            fba_fee=fba_fee,
        )
        == 10.0
    )


@pytest.mark.parametrize(
    "max_weight,product_weight,stock_level,min,max",
    (
        (200, 10, 5000, 5000, 20000),
        (200, 10, 50000, 20000, 20000),
        (50, 2, 3, 3, 25000),
        (50, 2, 26, 26, 25000),
    ),
)
def test_max_quantity(max_weight, product_weight, stock_level, min, max):
    region = mock.Mock(max_weight=max_weight)
    value = FBAPriceCalculator.get_max_quantity(
        region=region, product_weight=product_weight, stock_level=stock_level
    )
    assert value == (min, max)
