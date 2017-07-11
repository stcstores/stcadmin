from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from stcadmin import settings


def is_epos_user(user):
    return user.groups.filter(name__in=['epos'])


@login_required(login_url=settings.LOGIN_URL)
@user_passes_test(is_epos_user)
def index(request):
    return render(request, 'epos/index.html')
