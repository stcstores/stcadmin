from django.shortcuts import render
from django.contrib.auth.views import password_change
from django.contrib.auth import logout


def user(request):
    return render(request, 'user/user.html')


def change_password(request):
    return password_change(request, 'user/change_password.html')


def change_password_done(request):
    logout(request)
    return render(request, 'user/change_password_done.html')
