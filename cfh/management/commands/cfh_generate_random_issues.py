import random

from django.core.management import BaseCommand
from django.db.transaction import atomic

from issues.models import Issue, Service

nouns = [
    'trash can',
    'street',
    'bench',
    'lamp',
    'sign',
    'mailbox',
    'manhole cover',
]

adjectives = [
    '',
    '',
    'large',
    'small',
    'big',
    'tiny',
    'orange',
    'blue',
]

states = [
    'broken',
    'wet',
    'soaked',
    'nice',
    'trashed',
    'gone',
]

templates = [
    'The {adjective} {noun} is {state}',
    'Where has that {adjective} {noun} gone?',
    'Can you put an extra {noun} here?',
]


def generate_description():
    return random.choice(templates).format(
        noun=random.choice(nouns),
        adjective=random.choice(adjectives),
        state=random.choice(states),
    ).replace('  ', ' ')


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('-n', '--count', type=int, default=50)
        parser.add_argument('-s', '--service', required=True)
        parser.add_argument('--min-lat', type=float)
        parser.add_argument('--max-lat', type=float)
        parser.add_argument('--min-lon', type=float)
        parser.add_argument('--max-lon', type=float)

    @atomic
    def handle(self, count, service, min_lat=None, max_lat=None, min_lon=None, max_lon=None, **options):
        service = Service.objects.get(service_code=service)
        for i in range(count):
            lat = long = None
            if min_lat and max_lat and min_lon and max_lon:
                lat = random.uniform(min_lat, max_lat)
                long = random.uniform(min_lon, max_lon)

            issue = Issue(
                service=service,
                lat=lat,
                long=long,
                submitter_email='generate@example.com',
                description=generate_description(),
            )
            issue.save()
        self.stdout.write(f'{count} issues created')
