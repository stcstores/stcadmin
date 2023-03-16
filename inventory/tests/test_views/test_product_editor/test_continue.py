import pytest
from django.urls import reverse

from inventory.models import ProductRange


@pytest.fixture
def product_range(user, product_range_factory):
    return product_range_factory.create(status=ProductRange.CREATING, managed_by=user)


@pytest.fixture
def other_user(user_factory):
    return user_factory.create()


@pytest.fixture
def other_user_product_range(product_range_factory, other_user):
    return product_range_factory.create(
        status=ProductRange.CREATING, managed_by=other_user
    )


@pytest.fixture
def complete_user_product_range(user, product_range_factory):
    return product_range_factory.create(status=ProductRange.COMPLETE, managed_by=user)


@pytest.fixture
def complete_other_user_product_range(product_range_factory, other_user):
    return product_range_factory.create(
        status=ProductRange.COMPLETE, managed_by=other_user
    )


@pytest.fixture
def product_ranges(
    product_range,
    other_user_product_range,
    complete_user_product_range,
    complete_other_user_product_range,
):
    return


@pytest.fixture
def url():
    return reverse("inventory:continue")


@pytest.fixture
def get_response(group_logged_in_client, url):
    return group_logged_in_client.get(url)


@pytest.mark.django_db
def test_uses_template(get_response):
    assert "inventory/product_editor/continue.html" in (
        t.name for t in get_response.templates
    )


@pytest.mark.django_db
def test_user_product_ranges_in_context(product_ranges, product_range, get_response):
    assert list(get_response.context["user_product_ranges"]) == [product_range]


@pytest.mark.django_db
def test_others_product_ranges_in_context(
    product_ranges, other_user, other_user_product_range, get_response
):
    assert get_response.context["others_product_ranges"] == {
        other_user: [other_user_product_range]
    }
