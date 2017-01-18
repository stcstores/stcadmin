from stcadmin import settings
from django.shortcuts import render
from django.contrib.auth.views import password_change
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required


@login_required(login_url=settings.LOGIN_URL)
def user(request):
    return render(request, 'user/user.html')


@login_required(login_url=settings.LOGIN_URL)
def change_password(request):
    return password_change(request, 'user/change_password.html')


def change_password_done(request):
    logout(request)
    return render(request, 'user/change_password_done.html')
