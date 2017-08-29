from django.core.paginator import EmptyPage, Paginator
from django.core.urlresolvers import reverse_lazy
from django.shortcuts import get_object_or_404
from django.views.generic.base import TemplateView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.views.generic.list import ListView
from print_audit import forms, models

from .views import PrintAuditUserMixin


class UserFeedback(PrintAuditUserMixin, TemplateView):
    template_name = 'print_audit/user_feedback.html'

    def get(self, *args, **kwargs):
        self.form = forms.FeedbackDateFilterForm(initial={'dates': 'all'})
        super().get(*args, **kwargs)

    def post(self, *args, **kwargs):
        self.form = forms.FeedbackDateFilterForm(self.request.POST)
        super.post(*args, **kwargs)

    def get_context_data(self):
        self.get_models()
        self.date_filter()
        self.get_pack_counts()
        self.get_feedback_counts()
        return {
            'users': self.users, 'feedback_types': self.feedback_types,
            'feedback_counts': self.feedback_counts,
            'pack_counts': self.pack_counts, 'form': self.form}

    def get_pack_counts(self):
        self.pack_counts = {
            user.id: self.orders.filter(user=user).count() for user
            in self.users}

    def get_feedback_counts(self):
        feedback_counts = {}
        for user in self.users:
            feedback_counts[user.id] = {}
            for feedback_type in self.feedback_types:
                feedback_counts[user.id][
                    feedback_type.id] = self.feedback.filter(
                    user=user, feedback_type=feedback_type).count()

    def get_models(self):
        self.users = sorted(
            models.CloudCommerceUser.objects.all(),
            key=lambda x: x.full_name())
        self.feedback_types = models.Feedback.objects.all()
        self.orders = models.CloudCommerceOrder.objects.all()
        self.feedback = models.UserFeedback.objects.all()

    def date_filter(self):
        if self.form.is_valid():
            if self.form.cleaned_data['date_from'] is not None:
                date_range = (
                    self.form.cleaned_data['date_from'],
                    self.form.cleaned_data['date_to'])
                self.orders = self.orders.filter(
                    date_created__range=date_range)
                self.feedback = self.feedback.filter(
                    timestamp__range=date_range)


class CreateUserFeedback(PrintAuditUserMixin, CreateView):
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


class UpdateUserFeedback(PrintAuditUserMixin, UpdateView):
    model = models.UserFeedback
    fields = ['user', 'feedback_type', 'order_id', 'note']
    template_name = 'print_audit/user_feedback_form.html'
    success_url = reverse_lazy('print_audit:user_feedback')

    def get_object(self):
        return get_object_or_404(self.model, id=self.kwargs.get('feedback_id'))


class DeleteUserFeedback(PrintAuditUserMixin, DeleteView):
    model = models.UserFeedback

    def get_success_url(self):
        return self.request.META.get('HTTP_REFERER')


class SafePaginator(Paginator):
    def validate_number(self, number):
        try:
            return super(SafePaginator, self).validate_number(number)
        except EmptyPage:
            if number > 1:
                return self.num_pages
            else:
                raise


class FeedbackList(PrintAuditUserMixin, ListView):
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
        return context
