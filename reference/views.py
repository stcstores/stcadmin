from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.shortcuts import redirect
from django.core.exceptions import PermissionDenied
from django.urls import reverse

from stcadmin import settings


def index(request):
    return render(request, 'reference/index.html')


def shopify_tags(request):
    return render(request, 'reference/shopify_tags.html')
