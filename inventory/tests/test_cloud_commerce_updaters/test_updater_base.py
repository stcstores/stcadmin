from unittest.mock import patch

from home.tests.test_views.view_test import ViewTest
from inventory.tests.test_models.test_products import SetupVariationProductRange


class BaseUpdaterMethodTest(ViewTest):
    def update_DB_test(self):
        raise NotImplementedError

    def no_DB_update_test(self):
        raise NotImplementedError

    def update_CC_test(self):
        raise NotImplementedError

    def no_CC_update_test(self):
        self.assertEqual(0, len(self.mock_CCAPI.mock_calls))


class BaseUpdaterTest(SetupVariationProductRange):
    def setUp(self):
        super(SetupVariationProductRange, self).setUp()
        self.setup_products()
        self.updater = self.updater_class(self.updater_object(), self.user)
        self.setup_mock()
        self.update_updater()
        self.setup_test()

    def updater_object(self):
        raise NotImplementedError

    def setup_mock(self):
        ccapi_patcher = patch(self.patch_path)
        self.mock_CCAPI = ccapi_patcher.start()
        self.addCleanup(ccapi_patcher.stop)

    def setup_products(self):
        pass

    def update_updater(self):
        pass
