import pytz
from ccapi import CCAPI
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.utils.timezone import is_naive, now

USERS = CCAPI.get_users()


class CloudCommerceUser(models.Model):
    user_id = models.CharField(max_length=10, unique=True)
    stcadmin_user = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.CASCADE)

    def __init__(self, *args, **kwargs):
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
        return '{} {}'.format(self.first_name, self.second_name)

    def feedback_count(self, feedback_type):
        user_feedback = UserFeedback.objects.filter(
            user=self, feedback_type=feedback_type)
        return user_feedback.count()


class CloudCommerceOrder(models.Model):
    order_id = models.CharField(max_length=10, unique=True)
    user = models.ForeignKey(CloudCommerceUser, on_delete=models.CASCADE)
    date_created = models.DateTimeField()
    customer_id = models.CharField(max_length=10)
    trigger_id = models.CharField(max_length=10)
    date_completed = models.DateTimeField(blank=True, null=True)
    attempts = models.IntegerField()
    customer_order_dispatch_id = models.CharField(max_length=10)

    @classmethod
    def create_from_print_queue(cls, print_log):
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
        self.date_created = self.localise_datetime(self.date_created)
        if self.date_completed:
            self.date_completed = self.localise_datetime(self.date_completed)
        super(CloudCommerceOrder, self).save(*args, **kwargs)

    def localise_datetime(self, date_input):
        if date_input is not None and is_naive(date_input):
            tz = pytz.timezone('Europe/London')
            date_input = date_input.replace(tzinfo=tz)
        return date_input


class Feedback(models.Model):
    name = models.CharField(max_length=20)
    image = models.ImageField()
    score = models.IntegerField(default=0)

    def __str__(self):
        return self.name


class ScoredQuerySet(models.QuerySet):

    def score(self):
        return sum(o.feedback_type.score for o in self.all())


class UserFeedbackManager(models.Manager):

    def get_queryset(self):
        return ScoredQuerySet(self.model)


class UserFeedbackMonthlyManager(UserFeedbackManager):

    def get_queryset(self):
        return ScoredQuerySet(self.model).filter(timestamp__month=now().month)


class UserFeedback(models.Model):
    user = models.ForeignKey(CloudCommerceUser, on_delete=models.CASCADE)
    feedback_type = models.ForeignKey(Feedback, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(default=now)
    order_id = models.CharField(max_length=10, blank=True, null=True)
    note = models.TextField(blank=True, null=True)

    objects = UserFeedbackManager()
    this_month = UserFeedbackMonthlyManager()

    def __str__(self):
        return '{} for {}'.format(
            self.feedback_type.name, self.user.full_name())
