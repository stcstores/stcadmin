import datetime as dt

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


@pytest.mark.django_db
def test_barcode_available_attribute_defaults_to_true(new_barcode):
    assert new_barcode.available is True


@pytest.mark.django_db
def test_mark_used_method_marks_used(user, barcode_factory):
    barcode = barcode_factory.create(available=True)
    barcode.mark_used(user=user, used_for="test_text")
    barcode.refresh_from_db()
    assert barcode.available is False


@pytest.mark.django_db
def test_mark_used_method_sets_used_on(user, barcode_factory):
    barcode = barcode_factory.create(available=True)
    barcode.mark_used(user=user, used_for="test_text")
    barcode.refresh_from_db()
    assert type(barcode.used_on) == dt.datetime


@pytest.mark.django_db
def test_mark_used_method_sets_used_by(user, barcode_factory):
    barcode = barcode_factory.create(available=True)
    barcode.mark_used(user=user, used_for="test_text")
    barcode.refresh_from_db()
    assert barcode.used_by == user


@pytest.mark.django_db
def test_mark_used_method_sets_used_for(user, barcode_factory):
    barcode = barcode_factory.create(available=True)
    used_for = "test_text"
    barcode.mark_used(user=user, used_for=used_for)
    barcode.refresh_from_db()
    assert barcode.used_for == used_for


@pytest.mark.django_db
def test_mark_used_on_used_barcode_raises_exception(barcode_factory):
    barcode = barcode_factory.create(available=False)
    with pytest.raises(Barcode.BarcodeUsed):
        barcode.mark_used(user, used_for="test_text")


# @pytest.mark.django_db
# def test_get_barcode_method(self):
#     models.Barcode.objects.filter(barcode__in=["8114165461", "8114165462"]).update(
#         available=False, used_by=self.user, used_on=timezone.now()
#     )
#     expected_barcode = models.Barcode.objects.get(barcode="8114165463")
#     self.assertTrue(expected_barcode.available)
#     returned_barcode = models.Barcode.get_barcode(self.user, used_for="test_text")
#     self.assertEqual(returned_barcode, expected_barcode.barcode)
#     barcode = models.Barcode.objects.get(barcode=returned_barcode)
#     self.assertFalse(barcode.available)
#     self.assertIsNotNone(barcode.used_on)
#     self.assertEqual(barcode.used_by, self.user)
#     self.assertEqual(barcode.used_for, "test_text")


# @pytest.mark.django_db
# def test_get_barcodes_method(self):
#     models.Barcode.objects.filter(barcode__in=["8114165461", "8114165462"]).update(
#         available=False, used_by=self.user, used_on=timezone.now()
#     )
#     barcodes = models.Barcode.get_barcodes(
#         count=5, user=self.user, used_for="test_text"
#     )
#     self.assertEqual(
#         barcodes,
#         ["8114165463", "8114165464", "8114165465", "8114165466", "8114165467"],
#     )
#     queryset = models.Barcode.objects.filter(barcode__in=barcodes)
#     self.assertEqual(queryset.count(), 5)
#     for barcode in queryset:
#         self.assertFalse(barcode.available)
#         self.assertIsNotNone(barcode.used_on)
#         self.assertEqual(barcode.used_by, self.user)
#         self.assertEqual(barcode.used_for, "test_text")


# @pytest.mark.django_db
# def test_get_too_many_barcodes(self):
#     with self.assertRaises(models.Barcode.NotEnoughBarcodes):
#         models.Barcode.get_barcodes(count=500, user=self.user)
