from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from stcadmin import settings
from django.contrib.auth import logout


@login_required(login_url=settings.LOGIN_URL)
def index(request):
    return render(request, 'home/index.html')


def login_page(request, errors=[], messages=[]):
    return render(request, 'home/login.html', {
        'messages': messages, 'errors': errors})


def login_user(request):
    from django.contrib.auth import authenticate, login
    if request.user.is_authenticated():
        return redirect(reverse('home:index'))
    if 'username' in request.POST and 'password' in request.POST:
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect(reverse('home:index'))
        else:
            return login_page(request, errors=['Invalid login'])
    else:
        return login_page(request)


def logout_user(request):
    logout(request)
    return redirect(reverse('home:login_user'))
