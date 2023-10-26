import datetime as dt

import pytest
from django.urls import reverse

from restock.models import BlacklistedBrand


@pytest.fixture
def blacklisted_brand(blacklisted_brand_factory):
    blacklisted_brand = blacklisted_brand_factory.create()
    return blacklisted_brand


@pytest.mark.django_db
def test_blacklisted_brand_validates(blacklisted_brand):
    blacklisted_brand.full_clean()


@pytest.mark.django_db
def test_blacklisted_brand_has_name_attribute(blacklisted_brand):
    assert isinstance(blacklisted_brand.name, str)


@pytest.mark.django_db
def test_blacklisted_brand_has_comment_attribute(blacklisted_brand):
    assert isinstance(blacklisted_brand.comment, str)


@pytest.mark.django_db
def test_blacklisted_brand_has_created_at_attribute(blacklisted_brand):
    assert isinstance(blacklisted_brand.created_at, dt.datetime)


@pytest.mark.django_db
def test_blacklisted_brand_has_modified_at_attribute(blacklisted_brand):
    assert isinstance(blacklisted_brand.modified_at, dt.datetime)


@pytest.mark.django_db
def test_orders_by_name_by_default(blacklisted_brand_factory):
    blacklisted_brand_factory.create_batch(3)
    names = [_.name for _ in BlacklistedBrand.objects.all()]
    assert names == sorted(names)


@pytest.mark.django_db
def test_str_method(blacklisted_brand):
    assert str(blacklisted_brand) == blacklisted_brand.name


@pytest.mark.django_db
def test_fuzzy_search(blacklisted_brand_factory):
    close = blacklisted_brand_factory.create(name="Shaun")
    far = blacklisted_brand_factory.create(name="Sarah")
    qs = BlacklistedBrand.objects.fuzzy_search("Shawn")
    assert qs.contains(close)
    assert not qs.contains(far)


@pytest.mark.django_db
def test_get_absolute_url(blacklisted_brand):
    assert blacklisted_brand.get_absolute_url() == reverse(
        "restock:update_blacklisted_brand", args=[blacklisted_brand.pk]
    )
