from django.test import TestCase


class LabelMakerTemplateTest(TestCase):

    def template_test(self, url, template):
        response = self.client.get(url)
        self.assertTemplateUsed(response, template)

    def test_uses_index_template(self):
        self.template_test('/labelmaker', 'labelmaker/index.html')

    def test_uses_size_chart_form(self):
        self.template_test(
            '/create_size_chart_form/', 'labelmaker/size_chart_form.html')

        self.template_test(
            '/edit_size_chart_form/', 'labelmaker/size_chart_form.html')
