import pytest
from django.shortcuts import reverse


@pytest.fixture
def url():
    return "/fnac/translations/"


@pytest.fixture
def valid_get_response(valid_get_request, url):
    return valid_get_request(url)


@pytest.fixture
def valid_post_response(valid_post_request, url, post_data):
    return valid_post_request(url, post_data)


@pytest.fixture
def invalid_post_response(valid_post_request, url):
    return valid_post_request(url, {})


@pytest.fixture
def valid_get_response_content(valid_get_response):
    return valid_get_response.content.decode("utf8")


@pytest.fixture
def products(fnac_product_factory):
    return [
        fnac_product_factory.create(sku="5AM-8UM-7AN"),
        fnac_product_factory.create(sku="4AM-A1M-R2P"),
    ]


@pytest.fixture
def names():
    return ["Produit un titre", "Titre du produit deux"]


@pytest.fixture
def descriptions():
    return [
        "<p> Une description d'un produit </p>\r\n<p> Il est rouge </p>",
        "Une description d'un produit\r\nIl n'a pas de couleur",
    ]


@pytest.fixture
def colours():
    return ["rouge", ""]


@pytest.fixture
def translation_import_text():
    return "\r\n".join(
        [
            "SKU \tTitre \tCouleur \tLa description \t¬",
            "5 AM-8UM-7AN \tProduit un titre \trouge \t<p> Une description d'un produit </p>\r\n<p> Il est rouge </p> \t¬",
            "4 AM-A1M-R2P \tTitre du produit deux \tAucun \tUne description d'un produit\r\nIl n'a pas de couleur \t¬",
        ]
    )


@pytest.fixture
def post_data(translation_import_text):
    return {"translations": translation_import_text}


def test_logged_out_get_method(url, logged_in_client):
    response = logged_in_client.get(url)
    assert response.status_code == 403


def test_logged_out_get(client, url):
    response = client.get(url)
    assert response.status_code == 302


def test_logged_in_group_get(valid_get_response):
    assert valid_get_response.status_code == 200


@pytest.mark.django_db
def test_logged_in_post(url, logged_in_client, post_data):
    response = logged_in_client.post(url, post_data)
    assert response.status_code == 403


@pytest.mark.django_db
def test_logged_out_post(client, url, post_data):
    response = client.post(url, post_data)
    assert response.status_code == 302


@pytest.mark.django_db
def test_logged_in_group_post(group_logged_in_client, products, url, post_data):
    response = group_logged_in_client.post(url, post_data)
    assert response.status_code == 302


def test_heading(valid_get_response_content):
    text = "<h1>Add Translations</h1>"
    assert text in valid_get_response_content


@pytest.mark.django_db
def test_post_status_code(products, valid_post_response):
    assert valid_post_response.status_code == 302


@pytest.mark.django_db
def test_post_success_url(products, valid_post_response):
    assert valid_post_response.url == reverse("fnac:index")


@pytest.mark.django_db
def test_invalid_post_status_code(products, invalid_post_response):
    assert invalid_post_response.status_code == 200
    assert "translations" in invalid_post_response.content.decode("utf8")


@pytest.mark.django_db
def test_translation_created(products, valid_post_response):
    for product in products:
        product.refresh_from_db()
        assert product.translation is not None


@pytest.mark.django_db
def test_translation_names(products, names, valid_post_response):
    for product, name in zip(products, names):
        product.refresh_from_db()
        assert product.translation.name == name


@pytest.mark.django_db
def test_translation_descriptions(products, descriptions, valid_post_response):
    for product, description in zip(products, descriptions):
        product.refresh_from_db()
        assert product.translation.description == description


@pytest.mark.django_db
def test_translation_colours(products, colours, valid_post_response):
    for product, colour in zip(products, colours):
        product.refresh_from_db()
        assert product.translation.colour == colour


@pytest.mark.django_db
def test_product_missing_translation_count_in_content(
    products, valid_get_response_content
):
    assert (
        f"Products requiring translation: {len(products)}" in valid_get_response_content
    )


@pytest.mark.django_db
def test_empty_form_is_invalid(products, url, valid_post_request):
    response = valid_post_request(url, {"translations": ""})
    assert response.status_code == 200
    assert "This field is required" in response.content.decode("utf8")


@pytest.mark.django_db
@pytest.mark.parametrize(
    "input_text", ["invalid_text", "invalid_text\r\nmore invalid text"]
)
def test_single_line_of_text_is_rejected(products, url, valid_post_request, input_text):
    response = valid_post_request(url, {"translations": input_text})
    assert response.status_code == 200
    assert "No translations found" in response.content.decode("utf8")


@pytest.mark.django_db
def test_invalid_sku_input(products, url, valid_post_request, translation_import_text):
    products[0].sku = "AAA-AAA-AAA"
    products[0].save()
    response = valid_post_request(url, {"translations": translation_import_text})
    assert response.status_code == 200
    assert "No product with SKU 5AM-8UM-7AN exists" in response.content.decode("utf8")
