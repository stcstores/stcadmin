from inventory import forms, models
from inventory.tests.test_models.test_products import SetupProducts

from .form_test import FormTest


class TestProductSearchForm(SetupProducts, FormTest):
    RANGE_ID = "389839"

    def setUp(self):
        self.normal_range = models.ProductRange.objects.get(SKU=self.normal_range_SKU)
        self.eol_range = models.ProductRange.objects.get(SKU=self.eol_range_SKU)
        self.hidden_range = models.ProductRange.objects.get(SKU=self.hidden_range_SKU)

        self.normal_product = models.Product.objects.get(SKU=self.normal_product_SKU)
        self.eol_product = models.Product.objects.get(SKU=self.eol_product_SKU)
        self.hidden_product = models.Product.objects.get(SKU=self.hidden_product_SKU)

    @classmethod
    def create_ranges(cls):
        cls.normal_range_SKU = "RNG_939_ESA_383"
        cls.eol_range_SKU = "RNG_5D9_L3U_8LD"
        cls.hidden_range_SKU = "RNG_SEW_738_7GH"

        cls.normal_range = cls.new_product_range()
        cls.normal_range.range_ID = "4939943"
        cls.normal_range.SKU = cls.normal_range_SKU
        cls.normal_range.name = "Normal Range"
        cls.normal_range.save()

        cls.eol_range = cls.new_product_range()
        cls.eol_range.range_ID = "9841315"
        cls.eol_range.SKU = cls.eol_range_SKU
        cls.eol_range.end_of_line = True
        cls.eol_range.name = "EOL Range"
        cls.eol_range.save()

        cls.hidden_range = cls.new_product_range()
        cls.hidden_range.range_ID = "5751616"
        cls.hidden_range.SKU = cls.hidden_range_SKU
        cls.hidden_range.hidden = True
        cls.hidden_range.name = "Hidden Range"
        cls.hidden_range.save()

    @classmethod
    def add_products(cls):
        cls.normal_product_SKU = "JSL_48D_8TN"
        cls.eol_product_SKU = "8JR_L4B_JTE"
        cls.hidden_product_SKU = "BHN_DLC_GNB"

        normal_product = cls.new_product(cls.normal_range)
        normal_product.SKU = cls.normal_product_SKU
        normal_product.product_ID = "3490392"
        normal_product.save()

        eol_product = cls.new_product(cls.eol_range)
        eol_product.SKU = cls.eol_product_SKU
        eol_product.product_ID = "9841165"
        eol_product.supplier_SKU = "TESTSUPPLIERSKU"
        eol_product.save()

        hidden_product = cls.new_product(cls.hidden_range)
        hidden_product.SKU = cls.hidden_product_SKU
        hidden_product.product_ID = "986115616"
        hidden_product.save()

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
