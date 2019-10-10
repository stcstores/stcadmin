from django.utils import timezone

from inventory import models
from stcadmin.tests.stcadmin_test import STCAdminTest


class TestVATRate(STCAdminTest):
    @classmethod
    def setUpTestData(cls):
        cls.create_user()
        cls.timestamp = timezone.now()
        cls.stock_change = models.StockChange.objects.create(
            user=cls.user,
            product_sku="AXE-73D-N4Q",
            product_id="384093",
            stock_before=5,
            stock_after=7,
            timestamp=cls.timestamp,
        )

    def test_str_method(self):
        self.assertEqual(
            str(self.stock_change),
            (
                f"Stock for AXE-73D-N4Q changed by {self.user} at "
                f"{self.timestamp.strftime('%H:%M %d-%m-%Y')}"
            ),
        )

    def test_get_user_name_method(self):
        self.assertEqual(self.stock_change.get_user_name(), self.user.get_full_name())
