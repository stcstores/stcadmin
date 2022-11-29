from django.conf import settings

from home.templatetags import stcadmin_extras


def test_returns_scayt_customer_id():
    assert stcadmin_extras.scayt_customer_id() == settings.SCAYT_CUSTOMER_ID
