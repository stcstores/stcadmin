import json

from django.shortcuts import reverse

from inventory.models import Supplier
from labelmaker import forms, models, views
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


class TestCreateSizeChartView(LabelmakerViewTest, ViewTests):
    fixtures = ("labelmaker/labelmaker",)
    URL = "/labelmaker/product_labels/create_size_chart/"
    template = "labelmaker/sizechart_form.html"

    def setUp(self):
        super().setUp()
        self.name = "New Size Chart"
        self.supplier = Supplier.objects.get(id=1)

    def get_form_data(self):
        return {"name": self.name, "supplier": self.supplier.id}

    def make_post_request(self):
        return self.client.post(self.get_URL(), self.get_form_data())

    def test_get_method(self):
        response = self.make_get_request()
        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(response, self.template)

    def test_post_method(self):
        response = self.make_post_request()
        self.assertTrue(models.SizeChart.objects.filter(name="New Size Chart").exists())
        size_chart = models.SizeChart.objects.get(name="New Size Chart")
        self.assertEqual(self.name, size_chart.name)
        self.assertEqual(self.supplier, size_chart.supplier)
        self.assertRedirects(response, size_chart.get_edit_sizes_url())
        self.assertEqual(
            1, models.SizeChartSize.objects.filter(size_chart=size_chart).count()
        )


class TestUpdateSizeChartView(LabelmakerViewTest, ViewTests):
    fixtures = ("labelmaker/labelmaker",)
    template = "labelmaker/sizechart_form.html"

    def setUp(self):
        super().setUp()
        self.size_chart = models.SizeChart.objects.get(id=1)
        self.name = "New Size Chart"
        self.supplier = Supplier.objects.get(id=2)

    def get_URL(self, size_chart_id=None):
        if size_chart_id is None:
            size_chart_id = self.size_chart.id
        return f"/labelmaker/product_labels/update_size_chart/{size_chart_id}/"

    def get_form_data(self):
        return {"name": self.name, "supplier": self.supplier.id}

    def make_post_request(self):
        return self.client.post(self.get_URL(), self.get_form_data())

    def test_get_method(self):
        response = self.make_get_request()
        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(response, self.template)

    def test_post_method(self):
        self.assertNotEqual(self.size_chart.name, self.name)
        self.assertNotEqual(self.size_chart.supplier, self.supplier)
        response = self.make_post_request()
        size_chart = models.SizeChart.objects.get(id=self.size_chart.id)
        self.assertEqual(self.name, size_chart.name)
        self.assertEqual(self.supplier, size_chart.supplier)
        self.assertRedirects(response, size_chart.get_edit_sizes_url())


class TestDeleteSizeChartView(LabelmakerViewTest, ViewTests):
    fixtures = ("labelmaker/labelmaker",)
    template = "labelmaker/sizechart_confirm_delete.html"

    def setUp(self):
        super().setUp()
        self.size_chart = models.SizeChart.objects.get(id=1)

    def get_URL(self, size_chart_id=None):
        if size_chart_id is None:
            size_chart_id = self.size_chart.id
        return f"/labelmaker/product_labels/delete_size_chart/{size_chart_id}/"

    def test_get_method(self):
        response = self.make_get_request()
        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(response, self.template)
        self.assertIn(self.size_chart.name, str(response.content))
        self.assertIn(self.size_chart.supplier.name, str(response.content))
        self.assertIn("Are you sure", str(response.content))

    def test_post_method(self):
        response = self.make_post_request()
        self.assertRedirects(response, reverse("labelmaker:product_labels"))
        self.assertFalse(
            models.SizeChart.objects.filter(id=self.size_chart.id).exists()
        )

    def test_invalid_size_chart_id(self):
        response = self.client.get(self.get_URL(size_chart_id=99999))
        self.assertEqual(404, response.status_code)


class TestEditSizeChartSizes(LabelmakerViewTest, ViewTests):
    fixtures = ("labelmaker/labelmaker",)
    template = "labelmaker/size_chart_sizes.html"

    def setUp(self):
        super().setUp()
        self.size_chart = models.SizeChart.objects.get(id=1)
        self.sizes = models.SizeChartSize.objects.filter(size_chart=self.size_chart)

    def get_URL(self, size_chart_id=None):
        if size_chart_id is None:
            size_chart_id = self.size_chart.id
        return f"/labelmaker/product_labels/edit_size_chart_sizes/{size_chart_id}/"

    def make_post_request(self):
        return self.client.post(self.get_URL(), self.get_form_data())

    def get_form_data(self):
        form_data = {
            "sizechartsize_set-TOTAL_FORMS": len(self.sizes),
            "sizechartsize_set-INITIAL_FORMS": len(self.sizes),
            "sizechartsize_set-MIN_NUM_FORMS": 0,
            "sizechartsize_set-MAX_NUM_FORMS": 1,
        }
        for i, size in enumerate(self.sizes):
            form_data[f"sizechartsize_set-{i}-id"] = size.id
            form_data[f"sizechartsize_set-{i}-name"] = size.name
            form_data[f"sizechartsize_set-{i}-uk_size"] = size.uk_size
            form_data[f"sizechartsize_set-{i}-eu_size"] = size.eu_size
            form_data[f"sizechartsize_set-{i}-us_size"] = size.us_size
            form_data[f"sizechartsize_set-{i}-au_size"] = size.au_size
            form_data[f"sizechartsize_set-{i}-sort"] = size.sort
        return form_data

    def test_get_method(self):
        response = self.make_get_request()
        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(response, self.template)
        self.assertIn(self.size_chart.name, str(response.content))
        self.assertIn(self.size_chart.supplier.name, str(response.content))
        self.assertIn(self.size_chart.get_absolute_url(), str(response.content))
        self.assertIn("Add Size", str(response.content))
        self.assertIn("Save", str(response.content))
        self.assertIn("UK", str(response.content))
        self.assertIn("EUR", str(response.content))
        self.assertIn("US", str(response.content))
        self.assertIn("AUS", str(response.content))
        for size in self.sizes:
            self.assertIn(str(size.id), str(response.content))
            self.assertIn(size.name, str(response.content))
            self.assertIn(size.uk_size, str(response.content))
            self.assertIn(size.eu_size, str(response.content))
            self.assertIn(size.us_size, str(response.content))
            self.assertIn(size.au_size, str(response.content))

    def test_context(self):
        response = self.make_get_request()
        self.assertIsNotNone(response.context)
        self.assertIn("formset", response.context)
        self.assertIsInstance(response.context["formset"], forms.SizeFormset)
        self.assertIn("size_chart", response.context)
        self.assertEqual(self.size_chart, response.context["size_chart"])

    def test_empty_form(self):
        self.sizes.delete()
        response = self.make_get_request()
        self.assertIn(self.size_chart.name, str(response.content))
        self.assertIn(self.size_chart.supplier.name, str(response.content))
        self.assertIn(self.size_chart.name, str(response.content))
        self.assertIn(self.size_chart.get_absolute_url(), str(response.content))
        self.assertIn("Add Size", str(response.content))
        self.assertIn("Save", str(response.content))
        self.assertIn("UK", str(response.content))
        self.assertIn("EUR", str(response.content))
        self.assertIn("US", str(response.content))
        self.assertIn("AUS", str(response.content))
        for size in self.sizes:
            self.assertNotIn(str(size.id), str(response.content))
            self.assertNotIn(size.name, str(response.content))
            self.assertNotIn(size.uk_size, str(response.content))
            self.assertNotIn(size.eu_size, str(response.content))
            self.assertNotIn(size.us_size, str(response.content))
            self.assertNotIn(size.au_size, str(response.content))

    def test_post_method(self):
        response = self.make_post_request()
        self.assertRedirects(response, reverse("labelmaker:product_labels"))

    def test_size_update(self):
        new_name = "new_name"
        new_uk_size = "UK 5"
        new_eu_size = "EUR 5"
        new_us_size = "US 5"
        new_au_size = "AUD 5"
        self.assertNotEqual(new_name, self.sizes[0].name)
        self.assertNotEqual(new_uk_size, self.sizes[0].uk_size)
        self.assertNotEqual(new_eu_size, self.sizes[0].eu_size)
        self.assertNotEqual(new_us_size, self.sizes[0].us_size)
        self.assertNotEqual(new_au_size, self.sizes[0].au_size)
        form_data = self.get_form_data()
        form_data["sizechartsize_set-0-name"] = new_name
        form_data["sizechartsize_set-0-uk_size"] = new_uk_size
        form_data["sizechartsize_set-0-eu_size"] = new_eu_size
        form_data["sizechartsize_set-0-us_size"] = new_us_size
        form_data["sizechartsize_set-0-au_size"] = new_au_size
        self.client.post(self.get_URL(), form_data)
        size = models.SizeChartSize.objects.get(id=self.sizes[0].id)
        self.assertEqual(new_name, size.name)
        self.assertEqual(new_uk_size, size.uk_size)
        self.assertEqual(new_eu_size, size.eu_size)
        self.assertEqual(new_us_size, size.us_size)
        self.assertEqual(new_au_size, size.au_size)

    def test_invalid_size_chart_id(self):
        response = self.client.get(self.get_URL(size_chart_id=99999))
        self.assertEqual(404, response.status_code)


class TestCreateProductLabelsWithTemplateView(LabelmakerViewTest, ViewTests):
    fixtures = ("labelmaker/labelmaker",)
    template = "labelmaker/create_product_labels.html"

    def setUp(self):
        super().setUp()
        self.size_chart = models.SizeChart.objects.get(id=1)
        self.sizes = models.SizeChartSize.objects.filter(size_chart=self.size_chart)

    def get_URL(self, size_chart_id=None):
        if size_chart_id is None:
            size_chart_id = self.size_chart.id
        return f"/labelmaker/product_labels/create_product_labels/{size_chart_id}/"

    def test_get_method(self):
        response = self.make_get_request()
        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(response, self.template)

    def test_context(self):
        response = self.make_get_request()
        self.assertIsNotNone(response.context)
        self.assertIn("size_chart", response.context)
        self.assertEqual(self.size_chart, response.context["size_chart"])
        self.assertIn("sizes", response.context)
        self.assertCountEqual(self.sizes, response.context["sizes"])

    def test_content(self):
        response = self.make_get_request()
        self.assertIn("Product Code", str(response.content))
        self.assertIn("Create Table", str(response.content))
        self.assertIn(self.size_chart.name, str(response.content))
        self.assertIn(self.size_chart.supplier.name, str(response.content))
        for size in self.sizes:
            self.assertIn(size.name, str(response.content))
            self.assertIn(size.uk_size, str(response.content))

    def test_invalid_size_chart_id(self):
        response = self.client.get(self.get_URL(size_chart_id=99999))
        self.assertEqual(404, response.status_code)


class TestCreateProductLabelsWithoutTemplateView(LabelmakerViewTest, ViewTests):
    fixtures = ("labelmaker/labelmaker",)
    template = "labelmaker/create_product_labels.html"

    URL = "/labelmaker/product_labels/create_product_labels/"

    def test_get_method(self):
        response = self.make_get_request()
        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(response, self.template)

    def test_contents(self):
        response = self.make_get_request()
        self.assertIn("Product Code", str(response.content))
        self.assertIn("Create Table", str(response.content))


class TestProductLabelsPDFNoSizeChartView(LabelmakerViewTest, ViewTests):
    fixtures = ("labelmaker/labelmaker",)
    URL = "/labelmaker/product_labels/generate_product_labels/"

    def get_form_data(self):
        self.label_content = [
            {"size": "UK 5", "colour": "Green", "quantity": "1"},
            {"size": "UK 5", "colour": "Red", "quantity": "1"},
            {"size": "UK 6", "colour": "Green", "quantity": "1"},
            {"size": "UK 6", "colour": "Red", "quantity": "1"},
        ]
        self.product_code = "TV009"
        return {
            "data": json.dumps(self.label_content),
            "product_code": [self.product_code for _ in range(len(self.label_content))],
        }

    def make_post_request(self):
        return self.client.post(self.get_URL(), self.get_form_data())

    def test_post_method(self):
        response = self.make_post_request()
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.get("Content-Disposition"), 'filename="labels.pdf"')
        self.assertIn("PDF", str(response.content))


class TestProductLabelsPDFFromSizeChartView(LabelmakerViewTest, ViewTests):
    fixtures = ("labelmaker/labelmaker",)

    def get_URL(self, size_chart_id=None):
        if size_chart_id is None:
            size_chart_id = 1
        return f"/labelmaker/product_labels/generate_product_labels/{size_chart_id}/"

    def get_form_data(self):
        self.label_content = []
        for colour in ("Red", "Green"):
            for size in models.SizeChart.objects.get(id=1).sizechartsize_set.all():
                self.label_content.append(
                    {"size": size.id, "colour": colour, "quantity": "1"}
                )
        self.product_code = "TV009"
        return {
            "data": json.dumps(self.label_content),
            "product_code": [self.product_code for _ in range(len(self.label_content))],
        }

    def make_post_request(self):
        return self.client.post(self.get_URL(), self.get_form_data())

    def test_post_method(self):
        response = self.make_post_request()
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.get("Content-Disposition"), 'filename="labels.pdf"')
        self.assertIn("PDF", str(response.content))

    def test_invalid_size_chart_id(self):
        response = self.client.post(
            self.get_URL(size_chart_id=9999), self.get_form_data()
        )
        self.assertEqual(404, response.status_code)

    def test_invalid_size_id(self):
        form_data = self.get_form_data()
        form_data["data"] = json.dumps(
            [{"size": 9999, "colour": "Blue", "quantity": 1}]
        )
        response = self.client.post(self.get_URL(), form_data)
        self.assertEqual(404, response.status_code)

    def test_label_data_parsing(self):
        size_chart = models.SizeChart.objects.get(id=1)
        size = models.SizeChartSize.objects.get(id=1)
        label_data = views.ProductLabelsPDFFromSizeChart().get_label_data_for_size_chart(
            "TV009", [{"size": size.id, "colour": "Red", "quantity": 1}], size_chart
        )
        self.assertIsInstance(label_data, list)
        self.assertEqual(2, len(label_data))
        for item in label_data:
            self.assertIsInstance(item, list)
        label = ["Small", "Red", "TV009"]
        foreign_label = ["UK: 8-10", "EUR: 36-38", "USA: 4-6 AUS: 10-12"]
        self.assertEqual(label, label_data[0])
        self.assertEqual(foreign_label, label_data[1])

    def test_label_size_name(self):
        size_chart = models.SizeChart.objects.get(id=1)
        size = models.SizeChartSize.objects.get(id=1)
        size.name = ""
        size.save()
        label_data = views.ProductLabelsPDFFromSizeChart().get_label_data_for_size_chart(
            "TV009", [{"size": size.id, "colour": "Red", "quantity": 1}], size_chart
        )
        self.assertIsInstance(label_data, list)
        self.assertEqual(2, len(label_data))
        for item in label_data:
            self.assertIsInstance(item, list)
        label = ["UK: 8-10", "Red", "TV009"]
        self.assertEqual(label, label_data[0])


class TestTestProductPDFLabelView(LabelmakerViewTest, ViewTests):
    fixtures = ("labelmaker/labelmaker",)

    URL = "/labelmaker/product_labels/test/"

    def test_get_method(self):
        response = self.make_get_request()
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.get("Content-Disposition"), 'filename="labels.pdf"')
        self.assertIn("PDF", str(response.content))


class TestAddressLabelFormView(LabelmakerViewTest, ViewTests):

    URL = "/labelmaker/address_labels/"
    template = "labelmaker/address_label_form.html"

    def test_get_method(self):
        response = self.make_get_request()
        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(response, self.template)
        self.assertIn("Address Label", str(response.content))
        self.assertIn(reverse("labelmaker:address_label_pdf"), str(response.content))


class TestAddressLabelPDFView(LabelmakerViewTest, ViewTests):
    URL = "/labelmaker/address_labels/address_label_pdf/"
    label_contents = ["Address Line 1", "Address Line 2", "Address Line 3"]

    def get_form_data(self):
        return {"label_text": "\r\n".join(self.label_contents)}

    def make_post_request(self):
        return self.client.post(self.get_URL(), self.get_form_data())

    def test_post_method(self):
        response = self.make_post_request()
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.get("Content-Disposition"), 'filename="labels.pdf"')
        self.assertIn("PDF", str(response.content))

    def test_label_data(self):
        label_data = views.AddressLabelPDF().parse_label_data(
            "\r\n".join(self.label_contents)
        )
        self.assertEqual([self.label_contents], label_data)

    def test_empty_post(self):
        response = self.client.post(self.get_URL())
        self.assertEqual(404, response.status_code)


class TestSmallLabelFormView(LabelmakerViewTest, ViewTests):

    URL = "/labelmaker/small_labels/"
    template = "labelmaker/small_label_form.html"

    def test_get_method(self):
        response = self.make_get_request()
        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(response, self.template)
        self.assertIn("Small Label", str(response.content))


class TestSmallLabelPDFView(LabelmakerViewTest, ViewTests):
    URL = "/labelmaker/small_labels/small_label_pdf/"
    label_contents = ["Address Line 1", "Address Line 2", "Address Line 3"]

    def get_form_data(self):
        return {"label_text": ["\r\n".join(self.label_contents)], "quantity": [1]}

    def make_post_request(self):
        return self.client.post(self.get_URL(), self.get_form_data())

    def test_post_method(self):
        response = self.make_post_request()
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.get("Content-Disposition"), 'filename="labels.pdf"')
        self.assertIn("PDF", str(response.content))

    def test_label_data(self):
        text = ["\r\n".join(self.label_contents)]
        quantities = [1]
        label_data = views.SmallLabelPDF().parse_label_data(text, quantities)
        self.assertEqual(label_data, [self.label_contents])

    def test_label_quantity(self):
        text = ["\r\n".join(self.label_contents)]
        quantities = [2]
        label_data = views.SmallLabelPDF().parse_label_data(text, quantities)
        self.assertEqual(label_data, [self.label_contents, self.label_contents])

    def test_multiple_labels(self):
        first_label_contents = ["Line 1", "Line 2"]
        second_label_contents = ["First Line", "Second Line"]
        label_contents = (first_label_contents, second_label_contents)
        quantities = [2, 3]
        text = ["\r\n".join(_) for _ in label_contents]
        label_data = views.SmallLabelPDF().parse_label_data(text, quantities)
        self.assertEqual(
            label_data,
            [
                first_label_contents,
                first_label_contents,
                second_label_contents,
                second_label_contents,
                second_label_contents,
            ],
        )
