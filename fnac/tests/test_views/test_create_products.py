import pytest
from django.shortcuts import reverse
from pytest_django.asserts import assertTemplateUsed


class TestCreateProductsView:
    URL = "/fnac/create_products/"

    @pytest.fixture
    def products(self, fnac_product_factory, translation_factory):
        products = [
            fnac_product_factory.create(name="Missing Translation"),
            fnac_product_factory.create(created=True, name="Already created"),
            fnac_product_factory.create(description="", name="Missing description"),
            fnac_product_factory.create(price=None, name="Missing price"),
            fnac_product_factory.create(
                english_size="Large", french_size=None, price=556, name="Missing size"
            ),
            fnac_product_factory.create(price=None, name="Missing price"),
            fnac_product_factory.create(
                fnac_range__category=None, name="Missing category"
            ),
            fnac_product_factory.create(
                do_not_create=True, name="Marked do not create"
            ),
            fnac_product_factory.create(stock_level=0, name="Out of stock"),
            fnac_product_factory.create(name="Valid 2"),
        ]
        for product in products[1:]:
            translation_factory.create(product=product)
        return products

    @pytest.fixture
    def valid_get_response(self, valid_get_request):
        return valid_get_request(self.URL)

    @pytest.fixture
    def valid_get_response_content(self, valid_get_response):
        return valid_get_response.content.decode("utf8")

    def test_logged_out_get_method(self, logged_in_client):
        response = logged_in_client.get(self.URL)
        assert response.status_code == 403

    def test_logged_out_get(self, client):
        response = client.get(self.URL)
        assert response.status_code == 302

    def test_logged_in_group_get(self, valid_get_response):
        assert valid_get_response.status_code == 200

    def test_logged_in_post(self, logged_in_client):
        response = logged_in_client.post(self.URL)
        assert response.status_code == 403

    def test_logged_out_post(self, client):
        response = client.post(self.URL)
        assert response.status_code == 302

    def test_logged_in_group_post(self, group_logged_in_client):
        response = group_logged_in_client.post(self.URL)
        assert response.status_code == 405

    def test_templates_used(self, valid_get_response):
        assertTemplateUsed(valid_get_response, "fnac/create_products.html")
        assertTemplateUsed(
            valid_get_response, "fnac/status_boxes/inventory_update.html"
        )
        assertTemplateUsed(
            valid_get_response, "fnac/status_boxes/new_product_export_status.html"
        )

    def test_links_to_invalid_in_inventory(self, valid_get_response_content):
        assert (
            valid_get_response_content.count(reverse("fnac:invalid_in_inventory")) == 2
        )

    def test_links_to_missing_information(self, valid_get_response_content):
        assert (
            valid_get_response_content.count(reverse("fnac:missing_information")) == 2
        )

    def test_links_to_translations(self, valid_get_response_content):
        assert valid_get_response_content.count(reverse("fnac:translations")) == 2

    @pytest.mark.django_db
    def test_created_count_in_context(self, products, valid_get_response):
        assert valid_get_response.context["created_product_count"] == 1

    @pytest.mark.django_db
    def test_invalid_in_inventory_count_in_context(self, products, valid_get_response):
        assert valid_get_response.context["invalid_in_inventory_count"] == 1

    @pytest.mark.django_db
    def test_missing_information_count_in_context(self, products, valid_get_response):
        assert valid_get_response.context["missing_information_count"] == 4

    @pytest.mark.django_db
    def test_do_not_create_count_in_context(self, products, valid_get_response):
        assert valid_get_response.context["do_not_create_count"] == 1

    @pytest.mark.django_db
    def test_out_of_stock_count_in_context(self, products, valid_get_response):
        assert valid_get_response.context["out_of_stock_count"] == 1

    @pytest.mark.django_db
    def test_missing_translations_count_in_context(self, products, valid_get_response):
        assert valid_get_response.context["missing_translations_count"] == 1

    @pytest.mark.django_db
    def test_ready_to_create_count_in_context(self, products, valid_get_response):
        assert valid_get_response.context["ready_to_create_count"] == 1
