import datetime as dt
from unittest import mock

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


@pytest.fixture
def product(product_factory):
    return product_factory.create()


@pytest.fixture
def user(user_factory):
    return user_factory.create()


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


@pytest.fixture
def new_stock_level():
    return 4


class TestUpdateStockLevelMethod:
    @pytest.fixture
    def old_stock_level(self):
        return 5

    @pytest.fixture
    def source(self):
        return models.StockLevelHistory.IMPORT

    @pytest.fixture
    def previous_change(self, product, old_stock_level, stock_level_history_factory):
        return stock_level_history_factory.create(
            product=product, stock_level=old_stock_level
        )

    @pytest.fixture
    def created_stock_level_update(self, product, user, source, new_stock_level):
        return models.StockLevelHistory.objects._update_stock_level(
            product=product,
            stock_level=new_stock_level,
            source=source,
            user=user,
        )

    @pytest.mark.django_db
    def test_does_nothing_when_stock_level_has_not_changed(
        self, product, user, previous_change
    ):
        returned_value = models.StockLevelHistory.objects._update_stock_level(
            product=product,
            source=models.StockLevelHistory.IMPORT,
            stock_level=previous_change.stock_level,
            user=user,
        )
        assert returned_value is None
        assert models.StockLevelHistory.objects.filter(product=product).count() == 1

    @pytest.mark.django_db
    def test_creates_stock_level_history_object(self, created_stock_level_update):
        assert isinstance(created_stock_level_update, models.StockLevelHistory)
        assert isinstance(created_stock_level_update.id, int)

    @pytest.mark.django_db
    def test_sets_source(self, created_stock_level_update, source):
        assert created_stock_level_update.source == source

    @pytest.mark.django_db
    def test_sets_user(self, created_stock_level_update, user):
        assert created_stock_level_update.user == user

    @pytest.mark.django_db
    def test_sets_product(self, created_stock_level_update, product):
        assert created_stock_level_update.product == product

    @pytest.mark.django_db
    def test_sets_stock_level(self, created_stock_level_update, new_stock_level):
        assert created_stock_level_update.stock_level == new_stock_level

    @pytest.mark.django_db
    def test_sets_previous_change_to_none_when_not_found(
        self, created_stock_level_update, source
    ):
        assert created_stock_level_update.previous_change is None

    @pytest.mark.django_db
    def test_sets_previous_change_when_found(
        self, previous_change, created_stock_level_update, source
    ):
        assert created_stock_level_update.previous_change == previous_change


@pytest.fixture
def mock_update_stock_level_return_value():
    return mock.Mock()


@pytest.fixture
def mock_update_stock_level(mock_update_stock_level_return_value):
    with mock.patch(
        "inventory.models.stock_change.StockLevelHistoryManager._update_stock_level"
    ) as mock_update_stock_level:
        mock_update_stock_level.return_value = mock_update_stock_level_return_value
        yield mock_update_stock_level


@pytest.fixture
def mock_product():
    return mock.Mock()


@pytest.fixture
def mock_user():
    return mock.Mock()


def test_new_user_stock_level_update_method_calls_update_stock_level(
    mock_update_stock_level, new_stock_level, mock_product, mock_user
):
    models.StockLevelHistory.objects.new_user_stock_level_update(
        product=mock_product, user=mock_user, stock_level=new_stock_level
    )
    mock_update_stock_level.assert_called_once_with(
        product=mock_product,
        source=models.StockLevelHistory.USER,
        user=mock_user,
        stock_level=new_stock_level,
    )


def test_new_user_stock_level_update_returns_update_stock_level_return_value(
    mock_update_stock_level,
    mock_update_stock_level_return_value,
    new_stock_level,
    mock_product,
    mock_user,
):
    returned_value = models.StockLevelHistory.objects.new_user_stock_level_update(
        product=mock_product, user=mock_user, stock_level=new_stock_level
    )
    assert returned_value == mock_update_stock_level_return_value


def test_new_import_stock_level_update_method_calls_update_stock_level(
    mock_update_stock_level, new_stock_level, mock_product
):
    models.StockLevelHistory.objects.new_import_stock_level_update(
        product=mock_product, stock_level=new_stock_level
    )
    mock_update_stock_level.assert_called_once_with(
        product=mock_product,
        source=models.StockLevelHistory.IMPORT,
        user=None,
        stock_level=new_stock_level,
    )


def test_new_import_stock_level_update_returns_update_stock_level_return_value(
    mock_update_stock_level,
    mock_update_stock_level_return_value,
    new_stock_level,
    mock_product,
):
    returned_value = models.StockLevelHistory.objects.new_import_stock_level_update(
        product=mock_product, stock_level=new_stock_level
    )
    assert returned_value == mock_update_stock_level_return_value


def test_new_api_stock_level_update_method_calls_update_stock_level(
    mock_update_stock_level, new_stock_level, mock_product
):
    models.StockLevelHistory.objects.new_api_stock_level_update(
        product=mock_product, stock_level=new_stock_level
    )
    mock_update_stock_level.assert_called_once_with(
        product=mock_product,
        source=models.StockLevelHistory.API,
        user=None,
        stock_level=new_stock_level,
    )


def test_new_api_stock_level_update_returns_update_stock_level_return_value(
    mock_update_stock_level,
    mock_update_stock_level_return_value,
    new_stock_level,
    mock_product,
):
    returned_value = models.StockLevelHistory.objects.new_api_stock_level_update(
        product=mock_product, stock_level=new_stock_level
    )
    assert returned_value == mock_update_stock_level_return_value
