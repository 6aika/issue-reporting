import datetime
import string

from django.contrib.gis.db import models
from django.core.exceptions import ValidationError
from django.template.defaultfilters import truncatechars
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.utils.six import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

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
    location = models.PointField(srid=4326, blank=True, null=True, db_index=True)
    moderation = models.CharField(
        max_length=16, default='public', choices=MODERATION_STATUS_CHOICES, editable=False, db_index=True
    )

    def __str__(self):
        return "%s: %s" % (self.identifier, truncatechars(self.description, 50))

    def clean(self):
        self._cache_data()
        return super(Issue, self).clean()

    def save(self, **kwargs):
        self._cache_data()
        super(Issue, self).save(**kwargs)

    def _generate_identifier(self):
        for length in range(8, 65, 4):
            for attempt in range(10):
                id = get_random_string(length, allowed_chars=ID_KEYSPACE)
                if not Issue.objects.filter(identifier=id).exists():
                    # There's a minuscule chance of a race condition here, but the worst case
                    # is that the transaction fails and the client needs to try again.
                    return id

    def _cache_data(self):
        if not self.jurisdiction_id:
            from issues.models.jurisdictions import Jurisdiction
            self.jurisdiction = Jurisdiction.autodetermine()
        if not self.identifier:
            self.identifier = self._generate_identifier()
        if not self.service_id:
            from issues.models.services import Service
            self.service, created = Service.objects.get_or_create(service_code=self.service_code, defaults={
                'service_name': (getattr(self, 'service_name', None) or self.service_code)
            })
        if not self.service_code:
            self.service_code = self.service.service_code
        if not self.expected_datetime:
            from issues.analysis import calc_fixing_time
            fixing_time = calc_fixing_time(self.service_code)
            waiting_time = datetime.timedelta(milliseconds=fixing_time)
            self.expected_datetime = datetime.datetime.now() + waiting_time
