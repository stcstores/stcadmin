from inventory import forms, models
from inventory.tests import fixtures

from .form_test import FormTest


class TestProductSearchForm(fixtures.MultipleRangesFixture, FormTest):
    def test_form(self):
        data = {
            "search_term": "Range",
            "show_hidden": True,
            "supplier": self.supplier.id,
            "department": self.department.id,
            "end_of_line": forms.ProductSearchForm.INCLUDE_EOL,
        }
        form = forms.ProductSearchForm(data)
        self.assert_form_is_valid(form)
        self.assertDictEqual(
            {
                "search_term": "Range",
                "show_hidden": True,
                "supplier": self.supplier,
                "department": self.department,
                "end_of_line": forms.ProductSearchForm.INCLUDE_EOL,
            },
            form.cleaned_data,
        )

    def test_form_empty(self):
        form = forms.ProductSearchForm({})
        self.assert_form_is_valid(form)
        self.assertDictEqual(
            {
                "search_term": "",
                "show_hidden": False,
                "supplier": None,
                "department": None,
                "end_of_line": "",
            },
            form.cleaned_data,
        )
        self.assertEqual([], form.ranges)

    def product_search_form_test(self, expected, data):
        form = forms.ProductSearchForm(data)
        self.assert_form_is_valid(form)
        form.save()
        self.assertCountEqual(expected, form.ranges)

    def test_form_save(self):
        data = {"search_term": "Range"}
        expected = [self.normal_range, self.eol_range]
        self.product_search_form_test(expected, data)

    def test_form_search_term(self):
        data = {"search_term": "EOL"}
        expected = [self.eol_range]
        self.product_search_form_test(expected, data)

    def test_form_show_hidden(self):
        data = {"show_hidden": True}
        expected = [self.normal_range, self.eol_range, self.hidden_range]
        self.product_search_form_test(expected, data)

    def test_department_filter(self):
        product_range = self.eol_range
        product_range.department = models.Department.objects.get(id=2)
        product_range.save()
        data = {"department": self.eol_range.department.id}
        expected = [product_range]
        self.product_search_form_test(expected, data)

    def test_supplier_filter(self):
        product = self.eol_range.products()[0]
        product.supplier = models.Supplier.objects.get(id=2)
        product.save()
        data = {"supplier": product.supplier.id}
        expected = [self.eol_range]
        self.product_search_form_test(expected, data)

    def test_exclude_EOL(self):
        data = {"end_of_line": forms.ProductSearchForm.EXCLUDE_EOL}
        expected = [self.normal_range]
        self.product_search_form_test(expected, data)

    def test_only_EOL(self):
        data = {"end_of_line": forms.ProductSearchForm.ONLY_EOL}
        expected = [self.eol_range]
        self.product_search_form_test(expected, data)

    def test_search_by_range_SKU(self):
        data = {"search_term": self.eol_range.SKU}
        expected = [self.eol_range]
        self.product_search_form_test(expected, data)

    def test_search_by_range_ID(self):
        data = {"search_term": self.eol_range.range_ID}
        expected = [self.eol_range]
        self.product_search_form_test(expected, data)

    def test_search_by_product_SKU(self):
        data = {"search_term": self.eol_range.products()[0].SKU}
        expected = [self.eol_range]
        self.product_search_form_test(expected, data)

    def test_search_by_product_ID(self):
        data = {"search_term": self.eol_range.products()[0].product_ID}
        expected = [self.eol_range]
        self.product_search_form_test(expected, data)

    def test_search_by_product_supplier_SKU(self):
        data = {"search_term": self.eol_range.products()[0].supplier_SKU}
        expected = [self.eol_range]
        self.product_search_form_test(expected, data)

    def test_search_by_product_barcode(self):
        product = self.eol_range.products()[0]
        product.barcode = "9999999989"
        product.save()
        data = {"search_term": product.barcode}
        expected = [self.eol_range]
        self.product_search_form_test(expected, data)
