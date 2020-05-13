import json
from unittest.mock import patch

import pytest

from fnac import models
from fnac.forms import TranslationsForm


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


class TestTranslationsView:
    @pytest.fixture
    def url(self):
        return "/fnac/translations/"

    @pytest.fixture
    def valid_get_response(self, valid_get_request, url):
        return valid_get_request(url)

    @pytest.fixture
    def valid_get_response_content(self, valid_get_response):
        return valid_get_response.content.decode("utf8")

    def test_logged_out_get_method(self, url, logged_in_client):
        response = logged_in_client.get(url)
        assert response.status_code == 403

    def test_logged_out_get(self, client, url):
        response = client.get(url)
        assert response.status_code == 302

    def test_logged_in_group_get(self, valid_get_response):
        assert valid_get_response.status_code == 200

    @pytest.mark.django_db
    def test_logged_in_post(self, url, logged_in_client):
        response = logged_in_client.post(url)
        assert response.status_code == 403

    @pytest.mark.django_db
    def test_logged_out_post(self, client, url):
        response = client.post(url)
        assert response.status_code == 302

    @pytest.mark.django_db
    def test_logged_in_group_post(self, group_logged_in_client, products, url):
        response = group_logged_in_client.post(url)
        assert response.status_code == 405

    def test_heading(self, valid_get_response_content):
        text = "<h1>Add Translations</h1>"
        assert text in valid_get_response_content

    @pytest.mark.django_db
    def test_product_missing_translation_count_in_content(
        self, products, valid_get_response_content
    ):
        assert (
            f"Products requiring translation: {len(products)}"
            in valid_get_response_content
        )

    @pytest.mark.django_db
    def test_form_is_in_context(self, valid_get_response):
        assert isinstance(valid_get_response.context["form"], TranslationsForm)

    @pytest.mark.django_db
    def test_model_is_in_context(self, valid_get_response):
        assert (
            valid_get_response.context["TranslationUpdate"] == models.TranslationUpdate
        )


class TestUploadTranslationsView:
    @pytest.fixture
    def url(self):
        return "/fnac/translations/upload_translations/"

    @pytest.fixture
    def mock_create_update(self):
        with patch(
            "fnac.views.models.TranslationUpdate.objects.create_update"
        ) as mock_create_update:
            yield mock_create_update

    @pytest.fixture
    def post_data(self, translation_import_text):
        return {"translation_text": translation_import_text}

    @pytest.fixture
    def valid_post_response(
        self, mock_create_update, valid_post_request, url, post_data
    ):
        return valid_post_request(url, post_data)

    @pytest.fixture
    def invalid_post_response(self, valid_post_request, url):
        return valid_post_request(url, {})

    def test_logged_out_get_method(self, url, logged_in_client):
        response = logged_in_client.get(url)
        assert response.status_code == 403

    def test_logged_out_get(self, client, url):
        response = client.get(url)
        assert response.status_code == 302

    def test_logged_in_group_get(self, url, group_logged_in_client):
        response = group_logged_in_client.get(url)
        assert response.status_code == 405

    @pytest.mark.django_db
    def test_logged_in_post(self, url, logged_in_client, post_data):
        response = logged_in_client.post(url, post_data)
        assert response.status_code == 403

    @pytest.mark.django_db
    def test_post_status_code(self, products, valid_post_response):
        assert valid_post_response.status_code == 200

    @pytest.mark.django_db
    def test_post_response(self, valid_post_response):
        assert valid_post_response.content.decode("utf8") == "done"

    @pytest.mark.django_db
    def test_update_created(
        self, mock_create_update, translation_import_text, valid_post_response
    ):
        mock_create_update.assert_called_once_with(translation_import_text)

    @pytest.mark.django_db
    def test_invalid_post_status_code(self, products, invalid_post_response):
        assert invalid_post_response.status_code == 500

    @pytest.mark.django_db
    def test_empty_form_is_invalid(self, products, url, valid_post_request):
        response = valid_post_request(url, {"translation_text": ""})
        update = models.TranslationUpdate.objects.latest("timestamp")
        assert update.status == update.ERROR
        assert ["This field is required."] in update.errors.values()
        assert response.status_code == 500


class TestTranslationUpdateStatusView:
    @pytest.fixture
    def url(self):
        return "/fnac/translations/update_status/"

    @pytest.fixture
    def valid_get_response(self, url, valid_get_request):
        return valid_get_request(url)

    @pytest.fixture
    def valid_get_response_content(self, valid_get_response):
        return valid_get_response.content.decode("utf8")

    @pytest.fixture
    def existing_update(self, translation_update_factory):
        return translation_update_factory.create(
            status=models.TranslationUpdate.COMPLETE
        )

    @pytest.fixture
    def in_progress_update(self, translation_update_factory):
        return translation_update_factory.create(
            status=models.TranslationUpdate.IN_PROGRESS
        )

    @pytest.fixture
    def errored_update(self, translation_update_factory):
        return translation_update_factory.create(
            status=models.TranslationUpdate.ERROR, errors=["Error text"]
        )

    def test_logged_out_get_method(self, url, logged_in_client):
        response = logged_in_client.get(url)
        assert response.status_code == 403

    def test_logged_out_get(self, url, client):
        response = client.get(url)
        assert response.status_code == 302

    def test_logged_in_group_get(self, valid_get_response):
        assert valid_get_response.status_code == 200

    def test_logged_in_post(self, url, logged_in_client):
        response = logged_in_client.post(url)
        assert response.status_code == 403

    def test_logged_out_post(self, url, client):
        response = client.post(url)
        assert response.status_code == 302

    def test_logged_in_group_post(
        self, url, group_logged_in_client,
    ):
        response = group_logged_in_client.post(url)
        assert response.status_code == 405

    @pytest.mark.django_db
    def test_content_with_no_existing_update(self, valid_get_response_content):
        assert valid_get_response_content == json.dumps(
            {"status": None, "latest": None, "errors": None}
        )

    @pytest.mark.django_db
    def test_content_with_existing_update(
        self, existing_update, valid_get_response_content
    ):
        assert valid_get_response_content == json.dumps(
            {
                "status": models.TranslationUpdate.COMPLETE,
                "latest": existing_update.timestamp.strftime("%H:%M on %d %b %Y"),
                "errors": [],
            }
        )

    @pytest.mark.django_db
    def test_content_with_update_in_progress(
        self, in_progress_update, valid_get_response_content
    ):
        assert valid_get_response_content == json.dumps(
            {
                "status": models.TranslationUpdate.IN_PROGRESS,
                "latest": None,
                "errors": None,
            }
        )

    @pytest.mark.django_db
    def test_content_with_update_error(
        self, errored_update, valid_get_response_content
    ):
        assert valid_get_response_content == json.dumps(
            {
                "status": models.TranslationUpdate.ERROR,
                "latest": errored_update.timestamp.strftime("%H:%M on %d %b %Y"),
                "errors": errored_update.errors,
            }
        )
