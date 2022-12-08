from unittest import mock

import pytest

from inventory import models


def sku_test(text):
    assert text == text.upper()
    assert len(text) == 11
    assert text[3] == "-"
    assert text[7] == "-"
    for i, char in enumerate(text):
        if i in (3, 7):
            assert char == "-"
        else:
            assert char.isalnum()


def test_generate_sku():
    sku = models.product.generate_sku()
    sku_test(sku)


def test_generate_range_sku():
    sku = models.product.generate_range_sku()
    assert sku[:4] == "RNG_"
    sku_test(sku[4:])


def test_unique_sku_returns_sku_when_not_in_existing_skus():
    sku = "AAA-BBB-CCC"
    returned_value = models.product.unique_sku([], mock.Mock(return_value=sku))
    assert returned_value == sku


def test_unique_sku_retries_sku_generation_when_sku_in_existing_skus():
    skus = ["AAA-BBB-CCC", "BBB-CCC-DDD", "CCC-DDD-EEE"]
    mock_sku_generator = mock.Mock(side_effect=skus)
    models.product.unique_sku(skus[:-1], mock_sku_generator)
    assert mock_sku_generator.call_count == len(skus)


def test_unique_sku_errors_after_excessive_calls():
    sku = "AAA-BBB-CCC"
    mock_sku_generator = mock.Mock(return_value=sku)
    with pytest.raises(Exception):
        models.product.unique_sku([sku], mock_sku_generator)


@pytest.mark.django_db
@mock.patch("inventory.models.product.unique_sku")
def test_new_product_sku(mock_unique_sku, product_factory):
    product = product_factory.create()
    returned_value = models.product.new_product_sku()
    mock_unique_sku.assert_called_once_with(
        existing_skus={product.sku}, sku_function=models.product.generate_sku
    )
    assert returned_value == mock_unique_sku.return_value


@pytest.mark.django_db
@mock.patch("inventory.models.product.unique_sku")
def test_new_range_sku(mock_unique_sku, product_range_factory):
    product_range = product_range_factory.create()
    returned_value = models.product.new_range_sku()
    mock_unique_sku.assert_called_once_with(
        existing_skus={product_range.sku},
        sku_function=models.product.generate_range_sku,
    )
    assert returned_value == mock_unique_sku.return_value
