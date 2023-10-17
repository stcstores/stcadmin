import datetime as dt
from unittest.mock import call, patch

import pytest
from django.contrib.auth import get_user_model

from inventory import models


@pytest.fixture
def product_bay_history(product_bay_history_factory):
    product_bay_history = product_bay_history_factory.create()
    product_bay_history.full_clean()
    return product_bay_history


@pytest.fixture
def user(user_factory):
    return user_factory.create()


@pytest.fixture
def product(product_factory):
    return product_factory.create()


@pytest.fixture
def bay(bay_factory):
    return bay_factory.create()


@pytest.mark.django_db
def test_product_bay_history_has_user_attribute(product_bay_history):
    assert isinstance(product_bay_history.user, get_user_model())


@pytest.mark.django_db
def test_product_bay_history_has_timestamp_attribute(product_bay_history):
    assert isinstance(product_bay_history.timestamp, dt.datetime)


@pytest.mark.django_db
def test_product_bay_history_has_product_attribute(product_bay_history):
    assert isinstance(product_bay_history.product, models.Product)


@pytest.mark.django_db
def test_product_bay_history_has_bay_attribute(product_bay_history):
    assert isinstance(product_bay_history.bay, models.Bay)


@pytest.mark.django_db
def test_product_bay_history_change_attribute_can_be_added(product_bay_history_factory):
    product_bay_history = product_bay_history_factory.create(
        change=models.ProductBayHistory.ADDED
    )
    assert product_bay_history.change == models.ProductBayHistory.ADDED


@pytest.mark.django_db
def test_product_bay_history_change_attribute_can_be_removed(
    product_bay_history_factory,
):
    product_bay_history = product_bay_history_factory.create(
        change=models.ProductBayHistory.REMOVED
    )
    assert product_bay_history.change == models.ProductBayHistory.REMOVED


@pytest.mark.django_db
def test_product_bay_history_str_method(product_bay_history_factory):
    product_bay_history = product_bay_history_factory.create(
        product__product_range__name="Product Name",
        product__sku="AAA-AAA-AAA",
        bay__name="Bay Name",
        change=models.ProductBayHistory.ADDED,
    )
    assert (
        str(product_bay_history)
        == f"{product_bay_history.product} added {product_bay_history.bay}"
    )


class TestProductBayHistoryAddProductToBayMethod:
    @pytest.fixture
    def method_called(self, user, product, bay):
        models.ProductBayHistory.objects.add_product_to_bay(
            user=user, product=product, bay=bay
        )

    @pytest.mark.django_db
    def test_method_creates_product_bay_history_object(
        self, user, product, bay, method_called
    ):
        qs = models.ProductBayHistory.objects.filter(
            user=user,
            product=product,
            bay=bay,
            change=models.ProductBayHistory.ADDED,
        )
        assert qs.count() == 1

    @pytest.mark.django_db
    def test_method_creates_product_bay_link_object(self, product, bay, method_called):
        assert (
            models.ProductBayLink.objects.filter(product=product, bay=bay).count() == 1
        )


class TestProductBayHistoryRemoveProductFromBayMethod:
    @pytest.fixture
    def product_bay_link(self, product, bay):
        link = models.ProductBayLink(product=product, bay=bay)
        link.save()
        return link

    @pytest.fixture
    def method_called(self, user, product, bay):
        models.ProductBayHistory.objects.remove_product_from_bay(
            user=user, product=product, bay=bay
        )

    @pytest.mark.django_db
    def test_method_creates_product_bay_history_object(
        self, product_bay_link, user, product, bay, method_called
    ):
        qs = models.ProductBayHistory.objects.filter(
            user=user,
            product=product,
            bay=bay,
            change=models.ProductBayHistory.REMOVED,
        )
        assert qs.count() == 1

    @pytest.mark.django_db
    def test_method_deletes_product_bay_link(self, product_bay_link, method_called):
        qs = models.ProductBayLink.objects.filter(id=product_bay_link.id)
        assert qs.exists() is False


class TestProductBayHistorySetProductBaysMethod:
    @pytest.mark.django_db
    @patch(
        "inventory.models.location.ProductBayHistory.objects.remove_product_from_bay"
    )
    def test_method_calls_remove_product_from_bay(
        self, mock_remove_product_from_bay, user, product, product_bay_link_factory
    ):
        links = product_bay_link_factory.create_batch(3, product=product)
        models.ProductBayHistory.objects.set_product_bays(
            user=user, product=product, bays=[]
        )
        mock_remove_product_from_bay.assert_has_calls(
            (call(user=user, product=product, bay=link.bay) for link in links)
        )

    @pytest.mark.django_db
    @patch("inventory.models.location.ProductBayHistory.objects.add_product_to_bay")
    def test_method_calls_add_product_to_bay(
        self, mock_add_product_to_bay, user, product, bay_factory
    ):
        bays = bay_factory.create_batch(3)
        models.ProductBayHistory.objects.set_product_bays(
            user=user, product=product, bays=bays
        )
        mock_add_product_to_bay.assert_has_calls(
            (call(user=user, product=product, bay=bay) for bay in bays)
        )
