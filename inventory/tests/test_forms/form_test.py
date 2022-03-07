from stcadmin.tests.stcadmin_test import STCAdminTest


class FormTest(STCAdminTest):
    @classmethod
    def setUpTestData(cls):
        STCAdminTest.create_user()

    def assert_form_is_valid(self, form):
        self.assertTrue(form.is_valid(), f"Data: {form.data} Errors: {form.errors}")

    def assert_form_invalid(self, form):
        self.assertFalse(form.is_valid())
