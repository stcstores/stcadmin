import os
import json

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth import models
from django.core.exceptions import PermissionDenied
from stcadmin import settings
from django.contrib.auth.decorators import login_required, user_passes_test


def is_photo_user(user):
    return user.groups.filter(name__in=['photos'])


@login_required(login_url=settings.LOGIN_URL)
@user_passes_test(is_photo_user)
def index(request):
    if is_photo_user(request.user):
        return render(request, 'photos/index.html')
    return render(request, 'home/message.html', {
        'errors': ['You are not set up to recieve photos']})


@login_required(login_url=settings.LOGIN_URL)
@user_passes_test(is_photo_user)
def api_photo_list(request):
    if not is_photo_user(request.user):
        raise PermissionDenied("User not set up for photos")
    user_photo_dir = os.path.join(
        settings.MEDIA_ROOT, 'photo_organiser', request.user.username)
    photolist = [entry.name for entry in os.scandir(user_photo_dir) if
                 entry.is_file()]
    return HttpResponse(json.dumps(photolist))


@login_required(login_url=settings.LOGIN_URL)
@user_passes_test(is_photo_user)
def api_photo_delete(request):
    if not is_photo_user(request.user):
        raise PermissionDenied("User not set up for photos")
    image_filepath = os.path.join(
        settings.MEDIA_ROOT, 'photo_organiser', request.user.username,
        request.POST['filename'])
    if os.path.exists(image_filepath):
        os.remove(image_filepath)
        return HttpResponse(True)
    return HttpResponse(False)
