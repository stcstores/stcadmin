from home.tests.test_views.view_test import ViewTest


class FormTest(ViewTest):
    def assert_form_is_valid(self, form):
        self.assertTrue(form.is_valid(), f"Data: {form.data} Errors: {form.errors}")

    def assert_form_invalid(self, form):
        self.assertFalse(form.is_valid())
