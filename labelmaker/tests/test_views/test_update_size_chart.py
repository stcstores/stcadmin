import pytest
from django.urls import reverse
from requests_html import HTML

from labelmaker import models


@pytest.fixture
def path():
    return "labelmaker:update_size_chart"


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
def test_has_name_field(size_chart, html):
    assert html.find(f'input[name="name"][value={size_chart.name}]')


@pytest.mark.django_db
def test_has_supplier_field(html):
    assert html.find('select[name="supplier"]')


@pytest.mark.django_db
def test_supplier_field_containts_supplier(size_chart, html):
    assert html.find(
        f'option[value="{size_chart.supplier.id}"]', containing=size_chart.supplier.name
    )


@pytest.mark.django_db
def test_shows_suppliers(supplier_factory, get_html):
    supplier = supplier_factory.create()
    assert get_html().find(f'option[value="{supplier.id}"]', containing=supplier.name)


@pytest.mark.django_db
def test_form_submission_updates_size_chart(
    size_chart, supplier_factory, valid_client, url
):
    supplier = supplier_factory.create()
    name = "Size Chart Name"
    valid_client.post(url, {"supplier": supplier.id, "name": name})
    size_chart.refresh_from_db()
    assert size_chart.supplier == supplier
    assert size_chart.name == name


@pytest.mark.django_db
def test_form_submission_without_supplier(size_chart, valid_client, url):
    name = "Size Chart Name"
    valid_client.post(url, {"supplier": "", "name": name})
    size_chart.refresh_from_db()
    assert size_chart.supplier is None


@pytest.mark.django_db
def test_form_submission_without_name(valid_client, url):
    response = valid_client.post(url, {"supplier": "", "name": ""})
    assert response.status_code == 200


@pytest.mark.django_db
def test_redirect_after_submission(valid_client, url):
    name = "Test Name"
    response = valid_client.post(url, {"supplier": "", "name": name})
    assert response.status_code == 302
    expected_redirect = models.SizeChart.objects.get(name=name).get_edit_sizes_url()
    assert response["Location"] == expected_redirect
