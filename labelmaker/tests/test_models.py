from inventory.models import Supplier
from labelmaker import models
from stcadmin.tests.stcadmin_test import STCAdminTest


class TestSizeChart(STCAdminTest):
    size_chart_name = "New Size Chart"

    def setUp(self):
        self.supplier = Supplier.objects.create(
            name="Test Supplier", factory_ID="3893038", product_option_ID="384930"
        )

    def create_size_chart(self):
        return models.SizeChart.objects.create(
            name=self.size_chart_name, supplier=self.supplier
        )

    def test_create_size_chart(self):
        size_chart = self.create_size_chart()
        self.assertEqual(self.size_chart_name, size_chart.name)
        self.assertEqual(self.supplier, size_chart.supplier)
        self.assertEqual("Test Supplier - New Size Chart", str(size_chart))
        self.assertEqual(
            f"/labelmaker/size_chart_form/{size_chart.id}/",
            size_chart.get_absolute_url(),
        )
        self.assertEqual(
            f"/labelmaker/delete_size_chart/{size_chart.id}/",
            size_chart.get_delete_url(),
        )


class TestSizeChartSize(STCAdminTest):
    def setUp(self):
        self.supplier = Supplier.objects.create(
            name="Test Supplier", factory_ID="3893038", product_option_ID="384930"
        )
        self.size_chart = models.SizeChart.objects.create(
            name="New Size Chart", supplier=self.supplier
        )

    def test_size_chart_size(self):
        sort = 3
        name = "Large"
        uk_size = "UK 5"
        eu_size = "EU 37"
        us_size = "20"
        au_size = "45 AU"
        size = models.SizeChartSize.objects.create(
            size_chart=self.size_chart,
            sort=sort,
            name=name,
            uk_size=uk_size,
            eu_size=eu_size,
            us_size=us_size,
            au_size=au_size,
        )
        self.assertEqual(f"{self.size_chart.name} - UK {uk_size}", str(size))
        expected_size_list = (
            ("UK", uk_size),
            ("EUR", eu_size),
            ("USA", us_size),
            ("AUS", au_size),
        )
        self.assertEqual(expected_size_list, size.get_sizes())
