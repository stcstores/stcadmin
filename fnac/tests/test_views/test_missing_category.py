import pytest
from django.shortcuts import reverse


@pytest.fixture
def url():
    return "/fnac/missing_category/"


@pytest.fixture
def valid_get_response(valid_get_request, url):
    return valid_get_request(url)


@pytest.fixture
def valid_post_response(valid_post_request, url, post_data):
    return valid_post_request(url, post_data)


@pytest.fixture
def invalid_post_response(valid_post_request, url, post_data):
    post_data["form-0-category"] = "words"
    return valid_post_request(url, post_data)


@pytest.fixture
def valid_get_response_content(valid_get_response):
    return valid_get_response.content.decode("utf8")


@pytest.fixture
def new_category(category_factory):
    return category_factory.create()


@pytest.fixture
def fnac_range_without_category(fnac_range_factory, fnac_product_factory):
    def _fnac_range_without_category():
        fnac_range = fnac_range_factory.create(category=None)
        fnac_product_factory.create(fnac_range=fnac_range)
        fnac_product_factory.create(fnac_range=fnac_range)
        return fnac_range

    return _fnac_range_without_category


@pytest.fixture
def fnac_range_with_category(
    fnac_range_factory, category_factory, fnac_product_factory
):
    def _fnac_range_with_category():
        fnac_range = fnac_range_factory.create(
            category=category_factory.create(), name="Has Category"
        )
        fnac_product_factory.create(fnac_range=fnac_range)
        fnac_product_factory.create(fnac_range=fnac_range)
        return fnac_range

    return _fnac_range_with_category


@pytest.fixture
def out_of_stock_product_without_category(fnac_range_factory, fnac_product_factory):
    def _out_of_stock_product_without_category():
        fnac_range = fnac_range_factory.create(category=None, name="Out of Stock")
        fnac_product_factory.create(fnac_range=fnac_range, stock_level=0)
        return fnac_range

    return _out_of_stock_product_without_category


@pytest.fixture
def do_not_create_product_without_category(fnac_range_factory, fnac_product_factory):
    def _do_not_create_product_without_category():
        fnac_range = fnac_range_factory.create(category=None, name="Do Not Create")
        fnac_product_factory.create(fnac_range=fnac_range, do_not_create=True)
        return fnac_range

    return _do_not_create_product_without_category


@pytest.fixture
def created_product_without_category(fnac_range_factory, fnac_product_factory):
    def _created_product_without_category():
        fnac_range = fnac_range_factory.create(category=None, name="Created")
        fnac_product_factory.create(fnac_range=fnac_range, created=True)
        return fnac_range

    return _created_product_without_category


@pytest.fixture
def ranges_not_to_update(
    fnac_range_with_category,
    out_of_stock_product_without_category,
    do_not_create_product_without_category,
    created_product_without_category,
):
    return [
        fnac_range_with_category(),
        fnac_range_with_category(),
        out_of_stock_product_without_category(),
        do_not_create_product_without_category(),
        created_product_without_category(),
    ]


@pytest.fixture
def ranges_to_update(fnac_range_without_category):
    return [fnac_range_without_category() for i in range(5)]


@pytest.fixture
def post_data(ranges_to_update, new_category):
    range_count = len(ranges_to_update)
    form_data = {
        "form-TOTAL_FORMS": range_count,
        "form-INITIAL_FORMS": range_count,
        "form-MAX_NUM_FORMS": range_count,
    }
    for i, fnac_range in enumerate(ranges_to_update):
        form_data.update(
            {f"form-{i}-id": fnac_range.id, f"form-{i}-category": new_category.id}
        )
    return form_data


def test_logged_out_get_method(url, logged_in_client):
    response = logged_in_client.get(url)
    assert response.status_code == 403


def test_logged_out_get(client, url):
    response = client.get(url)
    assert response.status_code == 302


def test_logged_in_group_get(valid_get_response):
    assert valid_get_response.status_code == 200


def test_logged_in_post(url, logged_in_client):
    response = logged_in_client.post(url)
    assert response.status_code == 403


def test_logged_out_post(client, url):
    response = client.post(url)
    assert response.status_code == 302


@pytest.mark.django_db
def test_logged_in_group_post(
    group_logged_in_client, ranges_to_update, ranges_not_to_update, url, post_data
):
    response = group_logged_in_client.post(url, post_data)
    assert response.status_code == 302


def test_heading(valid_get_response_content):
    text = "<h1>Missing Categories</h1>"
    assert text in valid_get_response_content


@pytest.mark.django_db
def test_products_with_missing_category_displaid(
    ranges_to_update, ranges_not_to_update, valid_get_response_content
):
    for fnac_range in ranges_to_update:
        assert fnac_range.sku in valid_get_response_content
        assert fnac_range.name in valid_get_response_content


@pytest.mark.django_db
def test_products_with_category_not_displaid(
    ranges_to_update, ranges_not_to_update, valid_get_response_content
):
    for fnac_range in ranges_not_to_update:
        assert fnac_range.sku not in valid_get_response_content
        assert fnac_range.name not in valid_get_response_content


@pytest.mark.django_db
def test_post_status_code(ranges_not_to_update, ranges_to_update, valid_post_response):
    assert valid_post_response.status_code == 302


@pytest.mark.django_db
def test_post_success_url(ranges_not_to_update, ranges_to_update, valid_post_response):
    assert valid_post_response.url == reverse("fnac:index")


@pytest.mark.django_db
def test_categories_updated(
    ranges_not_to_update, ranges_to_update, valid_post_response, new_category
):
    for fnac_range in ranges_to_update:
        fnac_range.refresh_from_db()
        assert fnac_range.category == new_category


@pytest.mark.django_db
def test_invalid_post_status_code(
    ranges_not_to_update, ranges_to_update, invalid_post_response
):
    assert invalid_post_response.status_code == 200
    assert "category" in invalid_post_response.content.decode("utf8")


@pytest.mark.django_db
def test_category_is_not_required(
    ranges_not_to_update, ranges_to_update, valid_post_request, url, post_data
):
    post_data["form-1-category"] = ""
    response = valid_post_request(url, post_data)
    assert response.status_code == 302
