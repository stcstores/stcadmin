import datetime as dt

import pytest

from inventory.models import BaseProduct
from restock.models import Reorder


@pytest.fixture
def reorder(reorder_factory):
    reorder = reorder_factory.create()
    return reorder


@pytest.fixture
def closed_reorder(reorder_factory):
    reorder = reorder_factory.create(closed=True)
    return reorder


@pytest.fixture
def product(product_factory):
    return product_factory.create()


@pytest.fixture
def existing_open_reorder(product, reorder_factory):
    return reorder_factory.create(product=product)


@pytest.fixture
def existing_closed_reorder(product, reorder_factory):
    return reorder_factory.create(product=product, closed=True)


@pytest.fixture
def comment():
    return "Comment Text"


@pytest.mark.django_db
def test_reorder_validates(reorder):
    reorder.full_clean()


@pytest.mark.django_db
def test_reorder_has_product_attribute(reorder):
    assert isinstance(reorder.product, BaseProduct)


@pytest.mark.django_db
def test_reorder_has_count_attribute(reorder):
    assert isinstance(reorder.count, int)


@pytest.mark.django_db
def test_reorder_has_comment_attribute(reorder):
    assert isinstance(reorder.comment, str)


@pytest.mark.django_db
def test_reorder_has_created_at_attribute(reorder):
    assert isinstance(reorder.created_at, dt.datetime)


@pytest.mark.django_db
def test_reorder_has_modified_at_attribute(reorder):
    assert isinstance(reorder.modified_at, dt.datetime)


@pytest.mark.django_db
def test_reorder_has_closed_at_attribute(reorder):
    assert reorder.closed_at is None


@pytest.mark.django_db
def test_closed_reorder_closed_at_is_datetime_instance(closed_reorder):
    assert isinstance(closed_reorder.closed_at, dt.datetime)


@pytest.mark.django_db
def test_close_method(reorder):
    reorder.close()
    reorder.refresh_from_db()
    assert isinstance(reorder.closed_at, dt.datetime)


@pytest.mark.django_db
def test_open_filter(reorder, closed_reorder):
    qs = Reorder.objects.open()
    assert reorder in qs
    assert closed_reorder not in qs


@pytest.mark.django_db
def test_closed_filter(reorder, closed_reorder):
    qs = Reorder.objects.closed()
    assert closed_reorder in qs
    assert reorder not in qs


@pytest.mark.django_db
def test_set_count_creates_reorder(product):
    Reorder.objects.set_count(product, 5)
    assert Reorder.objects.get(product=product, count=5)


@pytest.mark.django_db
def test_set_count_returns_count(product):
    returned_value = Reorder.objects.set_count(product, 5)
    assert returned_value == 5


@pytest.mark.django_db
def test_set_count_updates_existing_reorder(existing_open_reorder):
    new_count = existing_open_reorder.count + 1
    Reorder.objects.set_count(existing_open_reorder.product, new_count)
    existing_open_reorder.refresh_from_db()
    assert existing_open_reorder.count == new_count


@pytest.mark.django_db
def test_set_count_cannot_set_count_to_zero_when_no_reorder_exists(product):
    with pytest.raises(Reorder.DoesNotExist):
        Reorder.objects.set_count(product, 0)


@pytest.mark.django_db
def test_set_count_closes_open_reorder_when_count_is_zero(existing_open_reorder):
    returned_value = Reorder.objects.set_count(existing_open_reorder.product, 0)
    existing_open_reorder.refresh_from_db()
    assert isinstance(existing_open_reorder.closed_at, dt.datetime)
    assert returned_value == 0


@pytest.mark.django_db
def test_set_count_does_not_update_closed_reorders(existing_closed_reorder):
    old_count = existing_closed_reorder.count
    Reorder.objects.set_count(
        existing_closed_reorder.product, existing_closed_reorder.count + 5
    )
    existing_closed_reorder.refresh_from_db()
    assert existing_closed_reorder.count == old_count


@pytest.mark.django_db
def test_set_comment_rasies_when_existing_reorder_does_not_exist(product):
    with pytest.raises(Reorder.DoesNotExist):
        Reorder.objects.set_comment(product, "Text")


@pytest.mark.django_db
def test_set_comment_rasies_when_only_closed_reorder_exists(existing_closed_reorder):
    with pytest.raises(Reorder.DoesNotExist):
        Reorder.objects.set_comment(existing_closed_reorder.product, "Text")


@pytest.mark.django_db
def test_set_comment_sets_comment(existing_open_reorder, comment):
    Reorder.objects.set_comment(existing_open_reorder.product, comment)
    existing_open_reorder.refresh_from_db()
    assert existing_open_reorder.comment == comment


@pytest.mark.django_db
def test_set_comment_returns_comment(existing_open_reorder, comment):
    returned_value = Reorder.objects.set_comment(existing_open_reorder.product, comment)
    assert returned_value == comment


@pytest.mark.django_db
def test_last_reorder_returns_none_when_no_reorder_exists(product):
    assert Reorder.objects.last_reorder(product) is None


@pytest.mark.django_db
def test_last_reorder_returns_most_recent_closed_reorder(
    product, existing_closed_reorder, existing_open_reorder
):
    assert Reorder.objects.last_reorder(product) == existing_closed_reorder


@pytest.mark.django_db
def test_last_reorder_returns_non_when_only_open_reorders_exist(
    existing_open_reorder, product
):
    assert Reorder.objects.last_reorder(product) is None
