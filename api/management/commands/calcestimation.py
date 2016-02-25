from datetime import timedelta

from django.core.management.base import BaseCommand, CommandError

from api.models import Feedback
from api.analysis import calc_fixing_time


class Command(BaseCommand):
    help = 'Fill the estimation of fixing'

    def handle(self, *args, **options):
        feedbacks = Feedback.objects.filter(expected_datetime__isnull=True)
        for f in feedbacks:
            fixing_time = calc_fixing_time(f.service_code)
            expected_datetime = f.requested_datetime + timedelta(milliseconds=fixing_time)
            f.expected_datetime = expected_datetime
            f.save()
        print("Estimation calculation completed")
