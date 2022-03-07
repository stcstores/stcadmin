from inventory import forms, models
from inventory.forms.product_order import ProductOrderForm
from inventory.tests import fixtures

from .form_test import FormTest


class TestProductOrderForm(FormTest, fixtures.VariationProductRangeFixture):
    fixtures = fixtures.VariationProductRangeFixture.fixtures

    def test_initial(self):
        form = ProductOrderForm(product=self.product)
        initial = form.get_initial()
        self.assertDictEqual(
            {
                "product_ID": self.product.product_ID,
                "range_order": self.product.range_order,
            },
            initial,
        )

    def test_submission(self):
        data = {"product_ID": self.product.product_ID, "range_order": 5}
        form = ProductOrderForm(data, product=self.product)
        self.assert_form_is_valid(form)
        self.assertDictEqual(
            {"product_ID": self.product.product_ID, "range_order": 5}, form.cleaned_data
        )

    def test_save_method(self):
        self.assertNotEqual(5, self.product.range_order)
        data = {"product_ID": self.product.product_ID, "range_order": 5}
        form = ProductOrderForm(data, product=self.product)
        self.assert_form_is_valid(form)
        form.save()
        product = models.Product.objects.get(id=self.product.id)
        self.assertEqual(5, product.range_order)


class TestProductOrderFormSet(fixtures.VariationProductRangeFixture, FormTest):
    def setUp(self):
        self.new_order = {
            variation.id: variation.range_order + 5 for variation in self.variations
        }

    def get_form_data(self):
        data = {"form-TOTAL_FORMS": len(self.variations), "form-INITIAL_FORMS": 0}
        for i, variation in enumerate(self.variations):
            data.update(
                {
                    f"form-{i}-product_ID": variation.product_ID,
                    f"form-{i}-range_order": self.new_order[variation.id],
                }
            )
        return data

    def test_formset(self):
        formset = forms.ProductOrderFormSet(
            self.get_form_data(), form_kwargs=[{"product": _} for _ in self.variations]
        )
        self.assert_form_is_valid(formset)
        for i, variation in enumerate(self.variations):
            self.assertDictEqual(
                {
                    "product_ID": variation.product_ID,
                    "range_order": variation.range_order + 5,
                },
                formset.cleaned_data[i],
            )

    def test_save_method(self):
        formset = forms.ProductOrderFormSet(
            self.get_form_data(), form_kwargs=[{"product": _} for _ in self.variations]
        )
        self.assert_form_is_valid(formset)
        for form in formset:
            form.save()
        for variation in self.variations:
            self.assertEqual(self.new_order[variation.id], variation.range_order)
