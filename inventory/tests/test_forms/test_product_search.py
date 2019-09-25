from inventory import forms
from inventory.tests.test_models.test_products import SetupProducts

from .form_test import FormTest


class TestProductSearchForm(SetupProducts, FormTest):
    RANGE_ID = "389839"

    def create_ranges(self):
        self.normal_range = self.new_product_range()
        self.normal_range.range_ID = "4939943"
        self.normal_range.SKU = "RNG_939_ESA_383"
        self.normal_range.name = "Normal Range"
        self.normal_range.save()

        self.eol_range = self.new_product_range()
        self.eol_range.range_ID = "9841315"
        self.eol_range.SKU = "RNG_5D9_L3U_8LD"
        self.eol_range.end_of_line = True
        self.eol_range.name = "EOL Range"
        self.eol_range.save()

        self.hidden_range = self.new_product_range()
        self.hidden_range.range_ID = "5751616"
        self.hidden_range.SKU = "RNG_SEW_738_7GH"
        self.hidden_range.hidden = True
        self.hidden_range.name = "Hidden Range"
        self.hidden_range.save()

    def add_products(self):
        self.normal_product = self.new_product(self.normal_range)
        self.normal_product.product_ID = "3490392"
        self.normal_product.save()

        self.eol_product = self.new_product(self.eol_range)
        self.eol_product.product_ID = "9841165"
        self.eol_product.supplier_SKU = "TESTSUPPLIERSKU"
        self.eol_product.save()

        self.hidden_product = self.new_product(self.hidden_range)
        self.hidden_product.product_ID = "986115616"
        self.hidden_product.save()

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
        self.eol_range.department = self.other_department
        self.eol_range.save()
        data = {"department": self.other_department.id}
        expected = [self.eol_range]
        self.product_search_form_test(expected, data)

    def test_supplier_filter(self):
        product = self.eol_range.products()[0]
        product.supplier = self.other_supplier
        product.save()
        data = {"supplier": self.other_supplier.id}
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
