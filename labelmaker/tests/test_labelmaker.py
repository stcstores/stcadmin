from django.contrib.auth.models import Group
from django.shortcuts import reverse

from stcadmin.tests.stcadmin_test import STCAdminTest


class LabelMakerTemplateTest(STCAdminTest):

    GROUP = "labelmaker"

    def setUp(self):
        self.create_user()
        group = Group.objects.get(name=self.GROUP)
        group.user_set.add(self.user)
        self.login_user()

    def test_uses_index_template(self):
        response = self.client.get(reverse("labelmaker:index"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "labelmaker/index.html")
