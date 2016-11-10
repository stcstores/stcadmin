from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.shortcuts import redirect
from django.core.exceptions import PermissionDenied
from django.urls import reverse

from stcadmin import settings
from shopify.models import MainCategory, SubCategory, Collection, Keyword


def index(request):
    return render(request, 'reference/index.html')


def shopify_tags(request):
    main_categories = MainCategory.objects.all()
    sub_categories = SubCategory.objects.all()
    collections = Collection.objects.all()
    keywords = Keyword.objects.all()
    return render(request, 'reference/shopify_tags.html', {
        'main_categories': main_categories,
        'sub_categories': sub_categories,
        'collections': collections,
        'keywords': keywords
    })
