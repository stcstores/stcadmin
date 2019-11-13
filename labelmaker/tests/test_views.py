from labelmaker import models
from stcadmin.tests.stcadmin_test import STCAdminTest, ViewTests


class LabelmakerViewTest(STCAdminTest):
    group_name = "labelmaker"

    def setUp(self):
        self.create_user()
        self.add_group("labelmaker")
        self.login_user()

    def remove_group(self):
        super().remove_group(self.group_name)


class TestIndexView(LabelmakerViewTest, ViewTests):
    URL = "/labelmaker/"
    template = "labelmaker/index.html"

    def test_get_method(self):
        response = self.make_get_request()
        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(response, self.template)

    def test_render(self):
        response = self.make_get_request()
        self.assertIn("Labelmaker", str(response.content))
        self.assertIn("Product Labels", str(response.content))
        self.assertIn("Address Labels", str(response.content))
        self.assertIn("Small Labels", str(response.content))


class TestProductLabelsView(LabelmakerViewTest, ViewTests):
    fixtures = ("labelmaker/labelmaker",)
    URL = "/labelmaker/product_labels/"
    template = "labelmaker/product_labels.html"

    def test_get_method(self):
        response = self.make_get_request()
        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(response, self.template)
        self.assertIn("Product Labels", str(response.content))
        for size_chart in models.SizeChart.objects.all():
            self.assertIn(size_chart.name, str(response.content))
            if size_chart.supplier is not None:
                self.assertIn(size_chart.supplier.name, str(response.content))
            self.assertIn(size_chart.get_delete_url(), str(response.content))
            self.assertIn(size_chart.get_edit_sizes_url(), str(response.content))
            self.assertIn(size_chart.get_use_url(), str(response.content))
        self.assertIn("Unknown Supplier", str(response.content))

    def test_context(self):
        response = self.make_get_request()
        self.assertIsNotNone(response.context)
        self.assertEqual(
            response.context["size_charts"], models.SizeChart.by_supplier()
        )
