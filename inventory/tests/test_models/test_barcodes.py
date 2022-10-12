import datetime as dt
from unittest.mock import patch

import pytest

from inventory.models import Barcode


@pytest.fixture
def barcode(barcode_factory):
    return barcode_factory.create()


@pytest.fixture
def user(user_factory):
    return user_factory.create()


@pytest.fixture
def barcodes(barcode_factory):
    return [barcode_factory.create() for i in range(50)]


@pytest.fixture
def new_barcode():
    barcode = Barcode(barcode="8114165461")
    barcode.save()
    return barcode


def test_barcode_barcode_attribute(barcode_factory):
    barcode = barcode_factory.build()
    assert isinstance(barcode.barcode, str)
    assert len(barcode.barcode) == 12
    assert barcode.barcode.isnumeric()


def test_available_barocde_available_attribute(barcode_factory):
    barcode = barcode_factory.build(used=False)
    assert barcode.available is True


def test_used_barocde_available_attribute(barcode_factory):
    barcode = barcode_factory.build(used=True)
    assert barcode.available is False


def test_barcode_available_attribute_defaults_to_true():
    barcode = Barcode(barcode="999999999999")
    assert barcode.available is True


class TestBarcodeMarkUsedMethod:
    @pytest.fixture
    def barcode_marked_used(self, user, barcode_factory):
        barcode = barcode_factory.create(used=False)
        barcode.mark_used(user=user, used_for="test_text")
        barcode.refresh_from_db()
        return barcode

    @pytest.mark.django_db
    def test_mark_used_method_sets_barcode_unavailable(self, barcode_marked_used):
        assert barcode_marked_used.available is False

    @pytest.mark.django_db
    def test_mark_used_method_sets_used_on(self, barcode_marked_used):
        assert isinstance(barcode_marked_used.used_on, dt.datetime)

    @pytest.mark.django_db
    def test_mark_used_method_sets_used_by(self, user, barcode_marked_used):
        assert barcode_marked_used.used_by == user

    @pytest.mark.django_db
    def test_mark_used_method_sets_used_for(self, barcode_marked_used):
        assert isinstance(barcode_marked_used.used_for, str)

    @pytest.mark.django_db
    def test_mark_used_on_used_barcode_raises_exception(self, user, barcode_factory):
        barcode = barcode_factory.create(used=True)
        with pytest.raises(Barcode.BarcodeUsed):
            barcode.mark_used(user, used_for="test_text")


class TestGetBarcodeMethod:
    @pytest.mark.django_db
    @patch("inventory.models.Barcode.get_barcodes")
    def test_calls_get_barcodes(self, mock_get_barcodes, user):
        Barcode.get_barcode(user=user)
        mock_get_barcodes.assert_called_once_with(count=1, user=user, used_for=None)

    @pytest.mark.django_db
    @patch("inventory.models.Barcode.get_barcodes")
    def test_takes_used_for_kwarg(self, mock_get_barcodes, user):
        used_for = "some text"
        Barcode.get_barcode(user=user, used_for=used_for)
        mock_get_barcodes.assert_called_once_with(count=1, user=user, used_for=used_for)


class TestGetBarcodesMethod:
    @pytest.mark.django_db
    def test_raises_if_not_enough_barcodes_are_available(self, user):
        with pytest.raises(Barcode.NotEnoughBarcodes):
            Barcode.get_barcodes(1, user=user)

    @pytest.mark.django_db
    def test_does_not_return_used_barcodes(self, user, barcode_factory):
        barcode_factory.create(used=True)
        with pytest.raises(Barcode.NotEnoughBarcodes):
            Barcode.get_barcodes(1, user=user)

    @pytest.mark.django_db
    def test_returns_available_barcode(self, user, barcode_factory):
        barcode = barcode_factory.create(used=False)
        return_value = Barcode.get_barcodes(1, user=user)
        assert return_value == [barcode.barcode]

    @pytest.mark.django_db
    def test_returns_requested_barcode_count(self, user, barcode_factory):
        barcode_factory.create_batch(10, used=False)
        return_value = Barcode.get_barcodes(5, user=user)
        assert len(return_value) == 5

    @pytest.mark.django_db
    def test_marks_returned_barcodes_used(self, user, barcode_factory):
        barcode = barcode_factory.create(used=False)
        Barcode.get_barcodes(1, user=user)
        barcode.refresh_from_db()
        assert barcode.available is False
        assert barcode.used_for is None
        assert barcode.used_on is not None

    @pytest.mark.django_db
    def test_takes_used_for_kwarg(self, user, barcode_factory):
        barcode = barcode_factory.create(used=False)
        used_for = "some text"
        Barcode.get_barcodes(1, user=user, used_for=used_for)
        barcode.refresh_from_db()
        assert barcode.used_for == used_for
