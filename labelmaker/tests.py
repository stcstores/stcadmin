"""Tests for labelmaker app."""

from django.test import TestCase


class LabelMakerTemplateTest(TestCase):
    """Tests for labelmaker templates."""

    def template_test(self, url, template):
        """Test url uses template."""
        response = self.client.get(url)
        self.assertTemplateUsed(response, template)

    def test_uses_index_template(self):
        """Test labelmaker index page uses the correct template."""
        self.template_test('/labelmaker', 'labelmaker/index.html')

    def test_uses_size_chart_form(self):
        """Test size chart pages use size chart form template."""
        self.template_test(
            '/create_size_chart_form/', 'labelmaker/size_chart_form.html')

        self.template_test(
            '/edit_size_chart_form/', 'labelmaker/size_chart_form.html')
