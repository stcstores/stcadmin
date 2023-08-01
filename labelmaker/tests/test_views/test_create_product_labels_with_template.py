import pytest
from django.urls import reverse
from requests_html import HTML


@pytest.fixture
def path():
    return "labelmaker:create_product_labels"


@pytest.fixture
def size_chart(size_chart_factory):
    return size_chart_factory.create()


@pytest.fixture
def size_chart_sizes(size_chart, size_chart_size_factory):
    return size_chart_size_factory.create_batch(3, size_chart=size_chart)


@pytest.fixture
def url(path, size_chart, size_chart_sizes):
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
def test_cannot_post(valid_client, url):
    assert valid_client.post(url).status_code == 405


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
def test_has_form(size_chart, html):
    target = reverse("labelmaker:generate_product_labels", args=[size_chart.id])
    assert html.find(f'form[action="{target}"][method="post"]')


@pytest.mark.django_db
def test_has_product_code_input(html):
    assert html.find('input[name="product_code"]')


@pytest.mark.django_db
def test_has_size_inputs(size_chart_sizes, html):
    for size in size_chart_sizes:
        assert html.find(f'input[name="size_{size.id}"][value="{size.id}"]')


@pytest.mark.django_db
def test_invalid_size_chart(valid_client, path):
    response = valid_client.get(reverse(path, args=[99999999999]))
    assert response.status_code == 404
