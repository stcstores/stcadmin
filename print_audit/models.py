"""Models for print_audit."""

import pytz
from ccapi import CCAPI
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.utils.timezone import is_naive, now


class UnHidden(models.Manager):
    """Manager for Cloud Commerce Users that are not hidden."""

    def get_queryset(self, *args, **kwargs):
        """Return queryset of Cloud Commerce Users that are not hidden."""
        queryset = super().get_queryset(*args, **kwargs)
        return queryset.filter(hidden=False)


class CloudCommerceUser(models.Model):
    """Model for storing details of Cloud Commerce Users."""

    user_id = models.CharField(max_length=10, unique=True)
    stcadmin_user = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.CASCADE)
    hidden = models.BooleanField(default=False)

    objects = models.Manager()
    unhidden = UnHidden()

    class Meta:
        """Meta class for CloudCommerceUser."""

        verbose_name = 'Cloud Commerce User'
        verbose_name_plural = 'Cloud Commerce Users'

    def __init__(self, *args, **kwargs):
        """Retrive user data from Cloud Commerce."""
        USERS = CCAPI.get_users()
        super(CloudCommerceUser, self).__init__(*args, **kwargs)
        try:
            self.cc_user = USERS[self.user_id]
        except IndexError:
            self.first_name = ''
            self.second_name = ''
        else:
            self.first_name = self.cc_user.first_name
            self.second_name = self.cc_user.second_name

    def __repr__(self):
        return self.full_name()

    def __str__(self):
        return self.full_name()

    def full_name(self):
        """Return user's full name."""
        return '{} {}'.format(self.first_name, self.second_name)

    def feedback_count(self, feedback_type):
        """Return number of feedback objects associated with user."""
        user_feedback = UserFeedback.objects.filter(
            user=self, feedback_type=feedback_type)
        return user_feedback.count()


class CloudCommerceOrder(models.Model):
    """Model for Cloud Commerce Orders."""

    order_id = models.CharField(max_length=10, unique=True)
    user = models.ForeignKey(CloudCommerceUser, on_delete=models.CASCADE)
    date_created = models.DateTimeField()
    customer_id = models.CharField(max_length=10)
    trigger_id = models.CharField(max_length=10)
    date_completed = models.DateTimeField(blank=True, null=True)
    attempts = models.IntegerField()
    customer_order_dispatch_id = models.CharField(max_length=10)

    class Meta:
        """Meta class for CloudCommerceOrder."""

        verbose_name = 'Cloud Commerce Order'
        verbose_name_plural = 'Cloud Commerce Orders'

    @classmethod
    def create_from_print_queue(cls, print_log):
        """Create CloudCommerceOrder from an entry in the print queue."""
        try:
            user = CloudCommerceUser.objects.get(
                user_id=str(print_log.user_id))
        except ObjectDoesNotExist:
            return
        cls.objects.create(
            order_id=str(print_log.order_id),
            user=user,
            date_created=print_log.date_created,
            trigger_id=str(print_log.trigger_id),
            attempts=int(print_log.attempts),
            date_completed=(print_log.date_completed),
            customer_order_dispatch_id=str(
                print_log.customer_order_dispatch_id))

    def save(self, *args, **kwargs):
        """Localise date created field."""
        self.date_created = self.localise_datetime(self.date_created)
        if self.date_completed:
            self.date_completed = self.localise_datetime(self.date_completed)
        super(CloudCommerceOrder, self).save(*args, **kwargs)

    def localise_datetime(self, date_input):
        """Return localised datetime.datetime object."""
        if date_input is not None and is_naive(date_input):
            tz = pytz.timezone('Europe/London')
            date_input = date_input.replace(tzinfo=tz)
        return date_input


class Feedback(models.Model):
    """Model for feedback scores."""

    name = models.CharField(max_length=20)
    image = models.ImageField(upload_to='feedback')
    score = models.IntegerField(default=0)

    class Meta:
        """Meta class for Feedback."""

        verbose_name = 'Feedback'
        verbose_name_plural = 'Feedback'

    def __str__(self):
        return self.name


class ScoredQuerySet(models.QuerySet):
    """Add score method to querysets for UserFeedback model."""

    def score(self):
        """Return accumulated score for feedback in queryset."""
        return sum(o.feedback_type.score for o in self.all())


class UserFeedbackManager(models.Manager):
    """
    Manager for UserFeedback model.

    Replaces QuerySet class with ScoredQuerySet.
    """

    def get_queryset(self):
        """Use ScoredQuerySet class in place of QuerySet."""
        return ScoredQuerySet(self.model)


class UserFeedbackMonthlyManager(UserFeedbackManager):
    """
    Manager for UserFeedback.

    Limits queries to feedback dated with in the current month.
    """

    def get_queryset(self):
        """Return QuerySet of User Feedback dated in the current month."""
        current_time = now()
        return ScoredQuerySet(self.model).filter(
            timestamp__month=current_time.month,
            timestamp__year=current_time.year)


class UserFeedback(models.Model):
    """Model to link CloudCommerceUser with Feedback."""

    user = models.ForeignKey(CloudCommerceUser, on_delete=models.CASCADE)
    feedback_type = models.ForeignKey(Feedback, on_delete=models.CASCADE)
    timestamp = models.DateField(default=now)
    order_id = models.CharField(max_length=10, blank=True, null=True)
    note = models.TextField(blank=True, null=True)

    objects = UserFeedbackManager()
    this_month = UserFeedbackMonthlyManager()

    class Meta:
        """Meta class for UserFeedback."""

        verbose_name = 'User Feedback'
        verbose_name_plural = 'User Feedback'

    def __str__(self):
        return '{} for {}'.format(
            self.feedback_type.name, self.user.full_name())


class Breakage(models.Model):
    """Model for storing details of product breakages."""

    product_sku = models.CharField(max_length=20)
    order_id = models.CharField(max_length=10)
    note = models.TextField(blank=True, null=True)
    packer = models.ForeignKey(CloudCommerceUser, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(default=now)

    class Meta:
        """Meta class for UserFeedback."""

        verbose_name = 'Breakage'
        verbose_name_plural = 'Breakages'
        ordering = ('timestamp', )

    def __str__(self):
        return '{} on order {}'.format(self.product_sku, self.order_id)
