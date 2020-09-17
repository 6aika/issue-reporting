import datetime
import string

from django.core.exceptions import ValidationError
from django.db import models
from django.template.defaultfilters import truncatechars
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.utils.six import python_2_unicode_compatible
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _

from issues.fields import GeoPointField

ID_KEYSPACE = string.ascii_lowercase + string.digits

STATUS_CHOICES = [
    ('open', _('open')),
    ('closed', _('closed')),
]

MODERATION_STATUS_CHOICES = [
    ('unmoderated', _('unmoderated')),
    ('public', _('public')),
    ('hidden', _('hidden')),
]


@python_2_unicode_compatible
class Issue(models.Model):
    application = models.ForeignKey('issues.Application', on_delete=models.PROTECT)
    jurisdiction = models.ForeignKey('issues.Jurisdiction', on_delete=models.PROTECT)
    service = models.ForeignKey('issues.Service')
    service_code = models.CharField(max_length=64, db_index=True)
    identifier = models.CharField(max_length=64, unique=True)
    description = models.TextField()
    status = models.CharField(max_length=32, blank=True, default='open', db_index=True, choices=STATUS_CHOICES)
    status_notes = models.TextField(blank=True)
    agency_responsible = models.CharField(max_length=140, blank=True)
    service_notice = models.TextField(blank=True)
    requested_datetime = models.DateTimeField(default=timezone.now)
    updated_datetime = models.DateTimeField(default=timezone.now)
    expected_datetime = models.DateTimeField(null=True)
    address = models.TextField(blank=True)
    zipcode = models.CharField(max_length=10, blank=True, db_index=True)
    media_url = models.URLField(blank=True)
    submitter_email = models.EmailField(blank=True)
    submitter_first_name = models.CharField(max_length=140, blank=True)
    submitter_last_name = models.CharField(max_length=140, blank=True)
    submitter_phone = models.CharField(max_length=140, blank=True)
    location = GeoPointField(blank=True, null=True, db_index=True)
    lat = models.FloatField(blank=True, null=True, db_index=True, editable=False)
    long = models.FloatField(blank=True, null=True, db_index=True, editable=False)
    moderation = models.CharField(
        max_length=16, default='public', choices=MODERATION_STATUS_CHOICES, editable=False, db_index=True
    )

    def __str__(self):
        return "{}: {}".format(self.identifier, truncatechars(self.description, 50))

    def clean(self):
        self._cache_data()

        if self.service.location_req == "coords_or_address":
            if not (self.location or self.address):
                raise ValidationError(
                    _('%(service)s requires coordinates or an address') % {'service': self.service}
                )

        elif self.service.location_req == "coords":
            if not self.location:
                raise ValidationError(
                    _('%(service)s requires coordinates') % {'service': self.service}
                )

        return super().clean()

    def save(self, **kwargs):
        self._cache_data()
        super().save(**kwargs)

    def _generate_identifier(self):
        for length in range(8, 65, 4):
            for attempt in range(10):
                id = get_random_string(length, allowed_chars=ID_KEYSPACE)
                if not Issue.objects.filter(identifier=id).exists():
                    # There's a minuscule chance of a race condition here, but the worst case
                    # is that the transaction fails and the client needs to try again.
                    return id

    def _cache_data(self):
        self._cache_location()

        if not self.application_id:
            from issues.models.applications import Application
            self.application = Application.autodetermine()

        if not self.jurisdiction_id:
            from issues.models.jurisdictions import Jurisdiction
            self.jurisdiction = Jurisdiction.autodetermine()

        if not self.identifier:
            self.identifier = self._generate_identifier()

        if not self.service_id:
            from issues.models.services import Service
            # TODO: There should probably be policy for and against this implicit service creation
            self.service, created = Service.objects.get_or_create(
                service_code=self.service_code,
                defaults={
                    'service_name': (getattr(self, 'service_name', None) or self.service_code),
                    'location_req': 'none',
                }
            )

        if not self.service_code:
            self.service_code = self.service.service_code

        if not self.expected_datetime:
            from issues.analysis import calc_fixing_time
            fixing_time = calc_fixing_time(self.service_code)
            waiting_time = datetime.timedelta(milliseconds=fixing_time)
            self.expected_datetime = now() + waiting_time

    def _cache_location(self):
        if (self.long and self.lat) and not self.location:
            from django.contrib.gis.geos import GEOSGeometry
            self.location = GEOSGeometry(
                f'SRID=4326;POINT({self.long} {self.lat})'
            )
        if self.location:
            self.long = self.location[0]
            self.lat = self.location[1]
        else:
            self.long = None
            self.lat = None
            self.location = None
