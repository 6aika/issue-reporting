import logging

from django.core.management import BaseCommand
from django.db.models import Q

from issues.geocoding import reverse_geocode
from issues.models import Issue

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Fill addresses for the issues with empty address_string field.'

    def handle(self, *args, **options):
        issues = Issue.objects.filter(Q(address_string__isnull=True) | Q(address_string__exact=''))
        for f in issues:
            if f.lat == 0 or f.lon == 0:
                continue
            address = reverse_geocode(f.lat, f.lon)
            f.address_string = address
            f.save()
        logger.info('reverse geocoding complete')
