import pytest
from django.urls import reverse
from requests_html import HTML

from labelmaker import models


@pytest.fixture
def path():
    return "labelmaker:edit_size_chart_sizes"


@pytest.fixture
def size_chart(size_chart_factory):
    return size_chart_factory.create()


@pytest.fixture
def size_chart_sizes(size_chart, size_chart_size_factory):
    return size_chart_size_factory.create_batch(3, size_chart=size_chart)


@pytest.fixture
def url(path, size_chart):
    return reverse(path, args=[size_chart.id])


@pytest.fixture
def get_page_text(valid_client, url):
    def _get_page_text():
        response = valid_client.get(url)
        return response.content.decode("utf8")

    return _get_page_text


@pytest.fixture
def page_text(get_page_text):
    return get_page_text()


@pytest.fixture
def html(page_text):
    return HTML(html=page_text)


@pytest.fixture
def get_html(get_page_text):
    def _get_html():
        return HTML(html=get_page_text())

    return _get_html


@pytest.fixture
def post_data(size_chart, size_chart_sizes):
    return {
        "sizechartsize_set-TOTAL_FORMS": "3",
        "sizechartsize_set-INITIAL_FORMS": "3",
        "sizechartsize_set-MIN_NUM_FORMS": "0",
        "sizechartsize_set-MAX_NUM_FORMS": "1",
        "sizechartsize_set-0-name": "Newborn",
        "sizechartsize_set-0-uk_size": "UK 0-0",
        "sizechartsize_set-0-eu_size": "0-15",
        "sizechartsize_set-0-us_size": "0-0",
        "sizechartsize_set-0-au_size": "0-0",
        "sizechartsize_set-0-sort": 1,
        "sizechartsize_set-0-id": size_chart_sizes[0].id,
        "sizechartsize_set-0-size_chart": size_chart.id,
        "sizechartsize_set-1-name": "Small",
        "sizechartsize_set-1-uk_size": "UK 0-2.5",
        "sizechartsize_set-1-eu_size": "15-18",
        "sizechartsize_set-1-us_size": "0-3.5",
        "sizechartsize_set-1-au_size": "0-2.5",
        "sizechartsize_set-1-sort": 2,
        "sizechartsize_set-1-id": size_chart_sizes[1].id,
        "sizechartsize_set-1-size_chart": size_chart.id,
        "sizechartsize_set-2-name": "Medium",
        "sizechartsize_set-2-uk_size": "UK 3-5.5",
        "sizechartsize_set-2-eu_size": "19-22",
        "sizechartsize_set-2-us_size": "4-6.5",
        "sizechartsize_set-2-au_size": "3-5.5",
        "sizechartsize_set-2-sort": 3,
        "sizechartsize_set-2-id": size_chart_sizes[2].id,
        "sizechartsize_set-2-size_chart": size_chart.id,
    }


@pytest.mark.django_db
def test_cannot_access_logged_out(logged_out_client, url):
    assert logged_out_client.get(url).status_code == 302


@pytest.mark.django_db
def test_cannot_access_if_not_in_group(client_not_in_group, url):
    assert client_not_in_group.get(url).status_code == 403


@pytest.mark.django_db
def test_can_post(valid_client, url):
    assert valid_client.post(url).status_code == 200


@pytest.mark.django_db
def test_page_contains_app_name(page_text):
    assert "Labelmaker" in page_text


@pytest.mark.django_db
@pytest.mark.parametrize(
    "reverse_path,text,count",
    (
        ("labelmaker:product_labels", "Product Labels", 1),
        ("labelmaker:address_labels", "Address Labels", 1),
        ("labelmaker:small_labels", "Small Labels", 1),
    ),
)
def test_has_links(reverse_path, text, count, html):
    target = reverse(reverse_path)
    elements = html.find(f'a[href="{target}"]', containing=text)
    assert len(elements) == count


@pytest.mark.django_db
def test_links_to_update_size_chart(size_chart, html):
    assert html.find(f'a[href="{size_chart.get_absolute_url()}"]')


@pytest.mark.django_db
def test_form_has_name_field(size_chart_sizes, html):
    for size_chart_size in size_chart_sizes:
        assert html.find(f'input[value="{size_chart_size.name}"]')


@pytest.mark.django_db
def test_form_has_uk_size_field(size_chart_sizes, html):
    for size_chart_size in size_chart_sizes:
        assert html.find(f'input[value="{size_chart_size.uk_size}"]')


@pytest.mark.django_db
def test_form_has_eu_size_field(size_chart_sizes, html):
    for size_chart_size in size_chart_sizes:
        assert html.find(f'input[value="{size_chart_size.eu_size}"]')


@pytest.mark.django_db
def test_form_has_us_size_field(size_chart_sizes, html):
    for size_chart_size in size_chart_sizes:
        assert html.find(f'input[value="{size_chart_size.us_size}"]')


@pytest.mark.django_db
def test_form_has_au_size_field(size_chart_sizes, html):
    for size_chart_size in size_chart_sizes:
        assert html.find(f'input[value="{size_chart_size.au_size}"]')


@pytest.mark.django_db
def test_form_has_delete_field(size_chart_sizes, html):
    for i, size_chart_size in enumerate(size_chart_sizes):
        assert html.find(f'input[name="sizechartsize_set-{i}-DELETE"]')


@pytest.mark.django_db
def test_form_submission(size_chart, post_data, size_chart_sizes, valid_client, url):
    valid_client.post(url, post_data)
    for i, size in enumerate(size_chart_sizes):
        size.refresh_from_db()
        assert size.name == post_data[f"sizechartsize_set-{i}-name"]
        assert size.uk_size == post_data[f"sizechartsize_set-{i}-uk_size"]
        assert size.us_size == post_data[f"sizechartsize_set-{i}-us_size"]
        assert size.au_size == post_data[f"sizechartsize_set-{i}-au_size"]
        assert size.eu_size == post_data[f"sizechartsize_set-{i}-eu_size"]
        assert size.sort == post_data[f"sizechartsize_set-{i}-sort"]


@pytest.mark.django_db
def test_form_creates_new_size(size_chart, size_chart_sizes, valid_client, url):
    data = {
        "sizechartsize_set-TOTAL_FORMS": "4",
        "sizechartsize_set-INITIAL_FORMS": "3",
        "sizechartsize_set-MIN_NUM_FORMS": "0",
        "sizechartsize_set-MAX_NUM_FORMS": "1",
        "sizechartsize_set-0-name": "Newborn",
        "sizechartsize_set-0-uk_size": "UK 0-0",
        "sizechartsize_set-0-eu_size": "0-15",
        "sizechartsize_set-0-us_size": "0-0",
        "sizechartsize_set-0-au_size": "0-0",
        "sizechartsize_set-0-sort": 1,
        "sizechartsize_set-0-id": size_chart_sizes[0].id,
        "sizechartsize_set-0-size_chart": size_chart.id,
        "sizechartsize_set-1-name": "Small",
        "sizechartsize_set-1-uk_size": "UK 0-2.5",
        "sizechartsize_set-1-eu_size": "15-18",
        "sizechartsize_set-1-us_size": "0-3.5",
        "sizechartsize_set-1-au_size": "0-2.5",
        "sizechartsize_set-1-sort": 2,
        "sizechartsize_set-1-id": size_chart_sizes[1].id,
        "sizechartsize_set-1-size_chart": size_chart.id,
        "sizechartsize_set-2-name": "Medium",
        "sizechartsize_set-2-uk_size": "UK 3-5.5",
        "sizechartsize_set-2-eu_size": "19-22",
        "sizechartsize_set-2-us_size": "4-6.5",
        "sizechartsize_set-2-au_size": "3-5.5",
        "sizechartsize_set-2-sort": 3,
        "sizechartsize_set-2-id": size_chart_sizes[2].id,
        "sizechartsize_set-2-size_chart": size_chart.id,
        "sizechartsize_set-3-name": "Large",
        "sizechartsize_set-3-uk_size": "UK 7",
        "sizechartsize_set-3-eu_size": "8",
        "sizechartsize_set-3-us_size": "9",
        "sizechartsize_set-3-au_size": "10",
        "sizechartsize_set-3-sort": 4,
        "sizechartsize_set-3-id": "",
        "sizechartsize_set-3-size_chart": size_chart.id,
    }
    valid_client.post(url, data)
    assert models.SizeChartSize.objects.filter(
        size_chart=size_chart,
        name="Large",
        uk_size="UK 7",
        eu_size="8",
        us_size="9",
        au_size="10",
        sort=4,
    ).exists


@pytest.mark.django_db
def test_invalid_form_submission(
    size_chart, post_data, size_chart_sizes, valid_client, url
):
    post_data["sizechartsize_set-0-uk_size"] = ""
    response = valid_client.post(url, post_data)
    assert response.status_code == 200


@pytest.mark.django_db
def test_redirect_after_submission(valid_client, url, post_data):
    response = valid_client.post(url, post_data)
    assert response.status_code == 302
    expected_redirect = reverse("labelmaker:product_labels")
    assert response["Location"] == expected_redirect
