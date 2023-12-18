import pytest
from django.urls import reverse

from inventory.models import ProductRange


@pytest.fixture
def url():
    def make_url(product_range_id):
        return reverse(
            "inventory:resume_editing_product", kwargs={"range_pk": product_range_id}
        )

    return make_url


@pytest.fixture
def get_response_for_product_id(group_logged_in_client, url):
    def make_get_response_for_product_id(product_id):
        return group_logged_in_client.get(url(product_id))

    return make_get_response_for_product_id


@pytest.mark.django_db
def test_response_with_non_existant_product_range(get_response_for_product_id):
    response = get_response_for_product_id(99999999)
    assert response.status_code == 404


@pytest.mark.django_db
def test_response_with_complete_product_range(
    get_response_for_product_id, product_range_factory
):
    product_range = product_range_factory.create(status=ProductRange.COMPLETE)
    response = get_response_for_product_id(product_range.id)
    assert response.status_code == 404


@pytest.mark.django_db
def test_response_with_errored_product_range(
    get_response_for_product_id, product_range_factory
):
    product_range = product_range_factory.create(status=ProductRange.ERROR)
    response = get_response_for_product_id(product_range.id)
    assert response.status_code == 404


@pytest.mark.django_db
def test_response_with_product_range_without_products(
    product_range_factory, get_response_for_product_id
):
    product_range = product_range_factory.create(status=ProductRange.CREATING)
    response = get_response_for_product_id(product_range.id)
    assert response.status_code == 302
    assert response["location"] == reverse(
        "inventory:create_initial_variation", kwargs={"range_pk": product_range.pk}
    )


@pytest.mark.django_db
def test_response_with_one_initial_variation(
    product_range_factory, initial_variation_factory, get_response_for_product_id
):
    product_range = product_range_factory.create(status=ProductRange.CREATING)
    initial_variation_factory.create(product_range=product_range)
    response = get_response_for_product_id(product_range.id)
    assert response.status_code == 302
    assert response["location"] == reverse(
        "inventory:setup_variations", kwargs={"range_pk": product_range.pk}
    )


@pytest.mark.django_db
def test_response_with_one_variation(
    product_range_factory, product_factory, get_response_for_product_id
):
    product_range = product_range_factory.create(status=ProductRange.CREATING)
    product_factory.create(product_range=product_range)
    response = get_response_for_product_id(product_range.id)
    assert response.status_code == 302
    assert response["location"] == reverse(
        "inventory:edit_new_product", kwargs={"range_pk": product_range.pk}
    )


@pytest.mark.django_db
def test_response_with_multiple_variations(
    product_range_factory, product_factory, get_response_for_product_id
):
    product_range = product_range_factory.create(status=ProductRange.CREATING)
    product_factory.create_batch(2, product_range=product_range)
    response = get_response_for_product_id(product_range.id)
    assert response.status_code == 302
    assert response["location"] == reverse(
        "inventory:edit_all_variations", kwargs={"range_pk": product_range.pk}
    )
