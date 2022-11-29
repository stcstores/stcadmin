from django.conf import settings

from home import views


def test_login_url():
    assert views.UserLoginMixin.login_url == settings.LOGIN_URL
