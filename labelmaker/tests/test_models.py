from inventory.models import Supplier
from labelmaker import models
from stcadmin.tests.stcadmin_test import STCAdminTest


class TestSizeChart(STCAdminTest):
    fixtures = ("labelmaker/labelmaker",)

    def setUp(self):
        super().setUp()
        self.size_chart = models.SizeChart.objects.get(id=1)

    def test_create_size_chart(self):
        size_chart_name = "New Size Chart"
        supplier = Supplier.objects.get(id=1)
        size_chart = models.SizeChart.objects.create(
            name=size_chart_name, supplier=supplier
        )
        self.assertEqual(size_chart_name, size_chart.name)
        self.assertEqual(supplier, size_chart.supplier)

    def test_str_method(self):
        self.assertEqual("Baum Trading - Ladies Clothing", str(self.size_chart))

    def test_str_method_without_supplier(self):
        size_chart = models.SizeChart.objects.filter(supplier__isnull=True)[0]
        self.assertEqual(size_chart.name, str(size_chart))

    def test_get_absolute_url_method(self):
        self.assertEqual(
            f"/labelmaker/product_labels/update_size_chart/1/",
            self.size_chart.get_absolute_url(),
        )

    def test_get_delete_url_method(self):
        self.assertEqual(
            f"/labelmaker/product_labels/delete_size_chart/1/",
            self.size_chart.get_delete_url(),
        )

    def test_get_edit_sizes_url(self):
        self.assertEqual(
            f"/labelmaker/product_labels/edit_size_chart_sizes/1/",
            self.size_chart.get_edit_sizes_url(),
        )

    def test_get_use_url(self):
        self.assertEqual(
            f"/labelmaker/product_labels/create_product_labels/1/",
            self.size_chart.get_use_url(),
        )

    def test_by_suppliers_method(self):
        suppliers_list = models.SizeChart.by_supplier()
        self.assertIsInstance(suppliers_list, dict)
        self.assertIn(Supplier.objects.get(id=1), suppliers_list)
        self.assertNotIn(Supplier.objects.get(id=4), suppliers_list)
        self.assertIn(None, suppliers_list)
        for key, value in suppliers_list.items():
            self.assertIsInstance(value, list)
            self.assertGreater(len(value), 0)
            for obj in value:
                self.assertIsInstance(obj, models.SizeChart)
            self.assertEqual(value, sorted(value, key=lambda x: x.name))


class TestSizeChartSize(STCAdminTest):
    fixtures = ("labelmaker/labelmaker",)

    def test_size_chart_size(self):
        size_chart = models.SizeChart.objects.get(id=1)
        sort = 3
        name = "Large"
        uk_size = "UK 5"
        eu_size = "EU 37"
        us_size = "20"
        au_size = "45 AU"
        size = models.SizeChartSize.objects.create(
            size_chart=size_chart,
            sort=sort,
            name=name,
            uk_size=uk_size,
            eu_size=eu_size,
            us_size=us_size,
            au_size=au_size,
        )
        self.assertEqual(f"{size_chart.name} - UK {uk_size}", str(size))
        expected_size_list = (
            ("UK", uk_size),
            ("EUR", eu_size),
            ("USA", us_size),
            ("AUS", au_size),
        )
        self.assertEqual(expected_size_list, size.get_sizes())
