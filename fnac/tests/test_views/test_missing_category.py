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
def invalid_ranges(fnac_range_factory):
    return [fnac_range_factory.create(category=None) for i in range(5)]


@pytest.fixture
def valid_ranges(fnac_range_factory, category_factory):
    return [
        fnac_range_factory.create(category=category_factory.create()) for i in range(5)
    ]


@pytest.fixture
def post_data(invalid_ranges, new_category):
    range_count = len(invalid_ranges)
    form_data = {
        "form-TOTAL_FORMS": range_count,
        "form-INITIAL_FORMS": range_count,
        "form-MAX_NUM_FORMS": range_count,
    }
    for i, fnac_range in enumerate(invalid_ranges):
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
    group_logged_in_client, invalid_ranges, valid_ranges, url, post_data
):
    response = group_logged_in_client.post(url, post_data)
    assert response.status_code == 302


def test_heading(valid_get_response_content):
    text = "<h1>Missing Categories</h1>"
    assert text in valid_get_response_content


@pytest.mark.django_db
def test_products_with_missing_category_displaid(
    invalid_ranges, valid_ranges, valid_get_response_content
):
    for fnac_range in invalid_ranges:
        assert fnac_range.sku in valid_get_response_content
        assert fnac_range.name in valid_get_response_content


@pytest.mark.django_db
def test_products_with_category_not_displaid(
    invalid_ranges, valid_ranges, valid_get_response_content
):
    for fnac_range in valid_ranges:
        assert fnac_range.sku not in valid_get_response_content
        assert fnac_range.name not in valid_get_response_content


@pytest.mark.django_db
def test_post_status_code(valid_ranges, invalid_ranges, valid_post_response):
    assert valid_post_response.status_code == 302


@pytest.mark.django_db
def test_post_success_url(valid_ranges, invalid_ranges, valid_post_response):
    assert valid_post_response.url == reverse("fnac:index")


@pytest.mark.django_db
def test_categories_updated(
    valid_ranges, invalid_ranges, valid_post_response, new_category
):
    for fnac_range in invalid_ranges:
        fnac_range.refresh_from_db()
        assert fnac_range.category == new_category


@pytest.mark.django_db
def test_invalid_post_status_code(valid_ranges, invalid_ranges, invalid_post_response):
    assert invalid_post_response.status_code == 200
    assert "category" in invalid_post_response.content.decode("utf8")


@pytest.mark.django_db
def test_category_is_not_required(
    valid_ranges, invalid_ranges, valid_post_request, url, post_data
):
    post_data["form-1-category"] = ""
    response = valid_post_request(url, post_data)
    assert response.status_code == 302
