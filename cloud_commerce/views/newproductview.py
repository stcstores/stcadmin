from django.core.urlresolvers import reverse_lazy
from django.views.generic.edit import FormView
from ccapi import CCAPI
import time


class NewProductView(FormView):
    success_url = reverse_lazy('cloud_commerce:index')
