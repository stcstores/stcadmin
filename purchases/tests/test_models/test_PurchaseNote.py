import datetime

import pytest

from purchases import models


@pytest.fixture
def text():
    return "Test purchase note text"


@pytest.fixture
def to_pay():
    return 0


@pytest.fixture
def purchase_user(user_factory):
    return user_factory.create()


@pytest.fixture
def created_by(user_factory):
    return user_factory.create()


@pytest.fixture
def new_purchase_note(to_pay, purchase_user, created_by, text):
    purchase_note = models.PurchaseNote(
        user=purchase_user, created_by=created_by, to_pay=to_pay, text=text
    )
    purchase_note.save()
    return purchase_note


@pytest.mark.django_db
def test_sets_user(purchase_user, new_purchase_note):
    assert new_purchase_note.user == purchase_user


@pytest.mark.django_db
def test_sets_created_at(new_purchase_note):
    assert isinstance(new_purchase_note.created_at, datetime.datetime)


@pytest.mark.django_db
def test_sets_modified_at(new_purchase_note):
    assert isinstance(new_purchase_note.modified_at, datetime.datetime)


@pytest.mark.django_db
def test_sets_created_by(created_by, new_purchase_note):
    assert new_purchase_note.created_by == created_by


@pytest.mark.django_db
def test_sets_to_pay(to_pay, new_purchase_note):
    assert new_purchase_note.to_pay == to_pay


@pytest.mark.django_db
def test_sets_cancelled(new_purchase_note):
    assert new_purchase_note.cancelled is False


@pytest.mark.django_db
def test_sets_text(new_purchase_note, text):
    assert new_purchase_note.text == text
