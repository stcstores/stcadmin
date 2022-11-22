import datetime as dt

import pytest
from django.contrib.auth import get_user_model

from inventory import models


@pytest.fixture
def stock_level_history(stock_level_history_factory):
    stock_level_history = stock_level_history_factory.create()
    stock_level_history.full_clean()
    return stock_level_history


@pytest.fixture
def new_stock_level_history(product_factory):
    product = product_factory.create()
    stock_level_history = models.StockLevelHistory(
        source=models.StockLevelHistory.IMPORT,
        product=product,
        stock_level=5,
    )
    stock_level_history.save()
    return stock_level_history


@pytest.mark.django_db
def test_has_source_attribute(stock_level_history):
    assert stock_level_history.source in (
        models.StockLevelHistory.USER,
        models.StockLevelHistory.IMPORT,
        models.StockLevelHistory.API,
    )


@pytest.mark.django_db
def test_has_user_attribute(stock_level_history):
    assert isinstance(stock_level_history.user, get_user_model())


@pytest.mark.django_db
def test_user_attribute_can_be_null(new_stock_level_history):
    assert new_stock_level_history.user is None


@pytest.mark.django_db
def test_product_attribute(stock_level_history):
    assert isinstance(stock_level_history.product, models.BaseProduct)


@pytest.mark.django_db
def test_has_stock_level_attribute(stock_level_history):
    assert isinstance(stock_level_history.stock_level, int)


@pytest.mark.django_db
def test_has_previous_change_attribute(stock_level_history):
    assert isinstance(stock_level_history.previous_change, models.StockLevelHistory)


@pytest.mark.django_db
def test_previous_change_attribute_can_be_null(new_stock_level_history):
    assert new_stock_level_history.previous_change is None


@pytest.mark.django_db
def test_has_timestamp_attribute(stock_level_history):
    assert isinstance(stock_level_history.timestamp, dt.datetime)
