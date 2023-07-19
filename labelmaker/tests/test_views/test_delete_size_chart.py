import pytest
from django.urls import reverse
from requests_html import HTML

from labelmaker import models


@pytest.fixture
def path():
    return "labelmaker:delete_size_chart"


@pytest.fixture
def size_chart(size_chart_factory):
    return size_chart_factory.create()


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


@pytest.mark.django_db
def test_cannot_access_logged_out(logged_out_client, url):
    assert logged_out_client.get(url).status_code == 302


@pytest.mark.django_db
def test_cannot_access_if_not_in_group(client_not_in_group, url):
    assert client_not_in_group.get(url).status_code == 403


@pytest.mark.django_db
def test_can_post(valid_client, url):
    assert valid_client.post(url).status_code == 302


@pytest.mark.django_db
def test_page_contains_app_name(size_chart, page_text):
    message = f'Are you sure you want to delete supplier "{str(size_chart)}"?'
    assert message in page_text


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
def test_form_submission_deletes_size_chart(size_chart, valid_client, url):
    valid_client.post(url)
    assert models.SizeChart.objects.filter(id=size_chart.id).exists() is False


@pytest.mark.django_db
def test_redirect_after_submission(valid_client, url):
    response = valid_client.post(url)
    assert response.status_code == 302
    expected_redirect = reverse("labelmaker:product_labels")
    assert response["Location"] == expected_redirect
