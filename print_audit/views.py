import json

from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.list import ListView
from django.core.urlresolvers import reverse_lazy
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse
from django.core.paginator import EmptyPage, Paginator
from django.utils.timezone import now
from django.db.models import Count
from django.db.models.functions import TruncDate

from stcadmin import settings
from print_audit import models
from print_audit import forms


def is_print_audit_user(user):
    return user.groups.filter(name__in=['print_audit'])


@login_required(login_url=settings.LOGIN_URL)
@user_passes_test(is_print_audit_user)
def index(request):
    return render(request, 'print_audit/index.html')


@login_required(login_url=settings.LOGIN_URL)
@user_passes_test(is_print_audit_user)
def user_feedback(request):
    users = models.CloudCommerceUser.objects.all()
    feedback_types = models.Feedback.objects.all()
    return render(
        request, 'print_audit/user_feedback.html',
        {'users': users, 'feedback_types': feedback_types})


class CreateUserFeedback(CreateView):
    model = models.UserFeedback
    fields = ['user', 'feedback_type', 'order_id', 'note']
    template_name = 'print_audit/user_feedback_form.html'
    success_url = reverse_lazy('print_audit:user_feedback')

    def get_initial(self):
        initial = super().get_initial()
        user_id = self.kwargs.get('user_id', None)
        if user_id is not None:
            initial['user'] = get_object_or_404(
                models.CloudCommerceUser, id=user_id)
        return initial


class UpdateUserFeedback(UpdateView):
    model = models.UserFeedback
    fields = ['user', 'feedback_type', 'order_id', 'note']
    template_name = 'print_audit/user_feedback_form.html'
    success_url = reverse_lazy('print_audit:user_feedback')

    def get_object(self):
        return get_object_or_404(self.model, id=self.kwargs.get('feedback_id'))


def delete_user_feedback(request, feedback_id):
    feedback = get_object_or_404(models.UserFeedback, id=feedback_id)
    feedback.delete()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


class SafePaginator(Paginator):
    def validate_number(self, number):
        try:
            return super(SafePaginator, self).validate_number(number)
        except EmptyPage:
            if number > 1:
                return self.num_pages
            else:
                raise


class FeedbackList(ListView):
    paginator_class = SafePaginator
    template_name = 'print_audit/feedback_list.html'
    model = models.UserFeedback
    paginate_by = 10
    context_object_name = 'feedback_list'
    user = None
    feedback_type = None

    def get(self, *args, **kwargs):
        user_id = self.request.GET.get('user_id') or None
        if user_id is not None:
            self.user = get_object_or_404(
                models.CloudCommerceUser, pk=user_id)
        feedback_id = self.request.GET.get('feedback_id') or None
        if feedback_id is not None:
            self.feedback_type = get_object_or_404(
                models.Feedback, pk=feedback_id)
        return super().get(*args, **kwargs)

    def post(self, *args, **kwargs):
        form = forms.FeedbackSearchForm(self.request.POST)
        if form.is_valid():
            self.user = form.cleaned_data.get('user') or None
            print(self.user)
            self.feedback_type = form.cleaned_data.get('feedback') or None
            self.paginate_by = form.cleaned_data.get(
                'paginate_by') or self.paginate_by
        return super().get(*args, **kwargs)

    def get_queryset(self):
        queryset = self.model.objects.all()
        if self.user is not None:
            queryset = queryset.filter(user=self.user)
        if self.feedback_type is not None:
            queryset = queryset.filter(feedback_type=self.feedback_type)
        queryset = queryset.order_by('-timestamp')
        return queryset

    def get_initial(self):
        initial = {}
        if self.user is not None:
            initial['user'] = self.user.pk
        if self.feedback_type is not None:
            initial['feedback'] = self.feedback_type.pk
        initial['paginate_by'] = self.paginate_by
        return initial

    def get_context_data(self):
        context = super().get_context_data()
        context['feedback_user'] = self.user
        context['feedback_type'] = self.feedback_type
        context['form'] = forms.FeedbackSearchForm(self.get_initial())
        print(self.get_initial())
        return context


def pack_count_monitor(request):
    orders = models.CloudCommerceOrder.objects.filter(
        date_created__year=now().year,
        date_created__month=now().month,
        date_created__day=now().day)
    packers = models.CloudCommerceUser.objects.all()
    pack_count = [
        (user.full_name(), orders.filter(user=user).count())
        for user in packers]
    pack_count = [
        count for count in pack_count if count[1] > 0]
    pack_count.sort(key=lambda x: x[1], reverse=True)
    return HttpResponse(json.dumps(pack_count))


def feedback_monitor(request):
    feedback_types = models.Feedback.objects.all()
    users = models.CloudCommerceUser.objects.all()
    data = []
    for user in users:
        counts = {}
        for f in feedback_types:
            count = models.UserFeedback.objects.filter(
                user=user, feedback_type=f,
                timestamp__month=now().month).count()
            counts[f.pk] = count
        if max(set(counts.values())) == 0:
            continue
        user_data = {'name': user.full_name(), 'feedback': []}
        for f in feedback_types:
            count = counts[f.pk]
            user_data['feedback'].append({
                'name': f.name, 'image_url': f.image.url, 'count': count})
        data.append(user_data)
    data.sort(
        key=lambda x: sum([f['count'] for f in x['feedback']]), reverse=True)
    return HttpResponse(json.dumps(data))


def display_monitor(request):
    return render(request, 'print_audit/display_monitor.html')


def charts(request):
    orders = models.CloudCommerceOrder.objects.all().extra(
        {'date': 'date(date_created)'}).values('date').annotate(
            count=Count('id')).order_by('-date')
    order_data = []
    for o in orders:
        order_data.append(
            {'date': o['date'].replace('-', ', '), 'count': o['count']})

    return render(request, 'print_audit/charts.html', {'orders': order_data})
