from django.utils import timezone

from home.tests.test_views.view_test import ViewTest
from inventory import models


class TestVATRate(ViewTest):
    def setUp(self):
        super().setUp()
        self.timestamp = timezone.now()
        self.stock_change = models.StockChange.objects.create(
            user=self.user,
            product_sku="AXE-73D-N4Q",
            product_id="384093",
            stock_before=5,
            stock_after=7,
            timestamp=self.timestamp,
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
