from unittest import mock

import pytest

from fba.models import profit


@pytest.fixture
def channel_sku():
    return "AAA_BBB_CCC_FBA"


@pytest.fixture
def asin():
    return "23402370709"


@pytest.fixture
def country():
    return "GB"


@pytest.fixture
def listing_name():
    return "Sale Item"


@pytest.fixture
def selling_price():
    return 502


@pytest.fixture
def total_fee():
    return 120


@pytest.fixture
def referral_fee():
    return 22


@pytest.fixture
def closing_fee():
    return 12


@pytest.fixture
def handling_fee():
    return 39


@pytest.fixture
def region(country, fba_region_factory):
    return fba_region_factory.create(country__ISO_code=country)


@pytest.fixture
def exchange_rate(region, exchange_rate_factory):
    return exchange_rate_factory.create(currency=region.currency)


@pytest.fixture
def fee(
    channel_sku,
    asin,
    country,
    listing_name,
    selling_price,
    total_fee,
    referral_fee,
    closing_fee,
    handling_fee,
):
    return profit._FBAFee(
        channel_sku=channel_sku,
        asin=asin,
        country=country,
        listing_name=listing_name,
        selling_price=selling_price,
        total_fee=total_fee,
        referral_fee=referral_fee,
        closing_fee=closing_fee,
        handling_fee=handling_fee,
    )


def test_fba_fee(
    channel_sku,
    asin,
    country,
    listing_name,
    selling_price,
    total_fee,
    referral_fee,
    closing_fee,
    handling_fee,
    fee,
):
    assert fee.channel_sku == channel_sku
    assert fee.asin == asin
    assert fee.country == country
    assert fee.listing_name == listing_name
    assert fee.selling_price == selling_price
    assert fee.total_fee == total_fee
    assert fee.referral_fee == referral_fee
    assert fee.closing_fee == closing_fee
    assert fee.handling_fee == handling_fee


@pytest.fixture
def mock_get_order_for_fee():
    with mock.patch("fba.models.profit._FBAProfitCalculation._get_order_for_fee") as m:
        yield m


@pytest.fixture
def mock_to_gbp():
    with mock.patch("fba.models.profit._FBAProfitCalculation._to_gbp") as m:
        yield m


@pytest.fixture
def mock_calculate_shipping_price():
    with mock.patch(
        "fba.models.profit._FBAProfitCalculation.calculate_shipping_price"
    ) as m:
        yield m


@pytest.fixture
def mock_profit():
    with mock.patch("fba.models.profit._FBAProfitCalculation._profit") as m:
        yield m


@pytest.fixture
def calculation(
    mock_get_order_for_fee,
    mock_to_gbp,
    mock_calculate_shipping_price,
    mock_profit,
    exchange_rate,
    region,
    fee,
):
    return profit._FBAProfitCalculation(fee)


@pytest.mark.django_db
def test_fba_profit_calculation_init(
    mock_get_order_for_fee,
    mock_to_gbp,
    mock_calculate_shipping_price,
    mock_profit,
    region,
    fee,
    calculation,
):
    mock_get_order_for_fee.assert_called_once_with()
    assert calculation.last_order == mock_get_order_for_fee.return_value
    assert calculation.product == mock_get_order_for_fee.return_value.product
    assert calculation.region == region
    assert calculation.exchange_rate == float(region.currency.exchange_rate())
    mock_to_gbp.assert_has_calls(
        [
            mock.call(region.placement_fee),
            mock.call(fee.selling_price),
            mock.call(fee.referral_fee),
            mock.call(fee.closing_fee),
            mock.call(fee.handling_fee),
        ]
    )
    assert calculation.placement_fee == mock_to_gbp.return_value
    assert calculation.sale_price == mock_to_gbp.return_value
    assert calculation.referral_fee == mock_to_gbp.return_value
    assert calculation.closing_fee == mock_to_gbp.return_value
    assert calculation.handling_fee == mock_to_gbp.return_value
    assert calculation.purchase_price == int(
        mock_get_order_for_fee.return_value.product.purchase_price * 100
    )
    assert calculation.shipping_price == mock_calculate_shipping_price.return_value
    assert calculation.profit == mock_profit.return_value


@pytest.mark.django_db
def test_calculate_shipping_price_method(
    mock_get_order_for_fee,
    mock_to_gbp,
    mock_profit,
    exchange_rate,
    region,
    fee,
):
    calculation = profit._FBAProfitCalculation(fee)
    calculation.region.calculate_shipping = mock.Mock(return_value=5)
    value = calculation.calculate_shipping_price()
    calculation.region.calculate_shipping.assert_called_once_with(
        calculation.product.weight_grams * calculation.last_order.quantity_sent
    )
    assert value == int(
        calculation.region.calculate_shipping.return_value
        / calculation.last_order.quantity_sent
    )


@pytest.mark.django_db
@mock.patch("fba.models.profit.FBAOrder")
def test_get_order_for_fee_method(
    mock_fba_order,
    mock_to_gbp,
    mock_calculate_shipping_price,
    mock_profit,
    exchange_rate,
    region,
    fee,
):
    calculation = profit._FBAProfitCalculation(fee)
    mock_fba_order.objects.fulfilled.assert_called_once_with()
    mock_fba_order.objects.fulfilled.return_value.filter.assert_called_once_with(
        product_asin=fee.asin
    )
    mock_fba_order.objects.fulfilled.return_value.filter.return_value.latest.assert_called_once_with(
        "closed_at"
    )
    assert (
        calculation.last_order
        == mock_fba_order.objects.fulfilled.return_value.filter.return_value.latest.return_value
    )


@pytest.mark.django_db
def test_to_gbp_method(
    mock_get_order_for_fee,
    mock_calculate_shipping_price,
    mock_profit,
    exchange_rate,
    region,
    fee,
):
    calculation = profit._FBAProfitCalculation(fee)
    calculation.exchange_rate = 2
    assert calculation._to_gbp(5.5) == 11.0


@pytest.mark.django_db
def test_costs_methods(calculation):
    calculation.placement_fee = 1.5
    calculation.referral_fee = 1.5
    calculation.closing_fee = 1.5
    calculation.handling_fee = 1.5
    calculation.purchase_price = 1.5
    calculation.shipping_price = 1.5
    assert calculation._costs() == 9.0


@pytest.mark.django_db
def test_profit_methods(
    mock_get_order_for_fee,
    mock_to_gbp,
    mock_calculate_shipping_price,
    exchange_rate,
    region,
    fee,
):
    calculation = profit._FBAProfitCalculation(fee)
    calculation._costs = mock.Mock(return_value=1.5)
    calculation.sale_price = 4.0
    assert calculation._profit() == 2.5
    calculation._costs.assert_called_once_with()


@pytest.mark.django_db
def test_to_object_method(calculation, fba_profit_file_factory, fba_order_factory):
    calculation.last_order = fba_order_factory.create()
    calculation.product = calculation.last_order.product
    import_record = fba_profit_file_factory.create()
    profit_object = calculation.to_object(import_record)
    assert profit_object.id is None
    assert profit_object.import_record == import_record
    assert profit_object.product == calculation.product
    assert profit_object.region == calculation.region
    assert profit_object.last_order == calculation.last_order
    assert profit_object.exchange_rate == calculation.exchange_rate
    assert profit_object.channel_sku == calculation.fee.channel_sku
    assert profit_object.asin == calculation.fee.asin
    assert profit_object.listing_name == calculation.fee.listing_name
    assert profit_object.sale_price == calculation.sale_price
    assert profit_object.referral_fee == calculation.referral_fee
    assert profit_object.closing_fee == calculation.closing_fee
    assert profit_object.handling_fee == calculation.handling_fee
    assert profit_object.placement_fee == calculation.placement_fee
    assert profit_object.purchase_price == calculation.purchase_price
    assert profit_object.shipping_price == calculation.shipping_price
    assert profit_object.profit == calculation.profit
