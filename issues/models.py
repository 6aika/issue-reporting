import string

from django.contrib.gis.db import models
from django.utils import timezone
from django.utils.crypto import get_random_string

ID_KEYSPACE = string.ascii_lowercase + string.digits


class MultipleJurisdictionsError(ValueError):
    pass


class Jurisdiction(models.Model):
    identifier = models.CharField(max_length=64, unique=True)
    name = models.CharField(max_length=64)

    @staticmethod
    def autodetermine():
        jurisdiction_count = Jurisdiction.objects.count()
        if jurisdiction_count == 0:
            return Jurisdiction.objects.create(
                identifier="default",
                name="Default"
            )
        elif jurisdiction_count == 1:
            return Jurisdiction.objects.first()
        raise MultipleJurisdictionsError("Jurisdiction must be chosen (there are %d)" % jurisdiction_count)


class Issue(models.Model):
    jurisdiction = models.ForeignKey("issues.Jurisdiction", on_delete=models.PROTECT)
    service = models.ForeignKey("issues.Service")
    service_request_id = models.CharField(max_length=64, unique=True)
    status_notes = models.TextField(blank=True, default="")
    status = models.TextField(blank=True, default="")
    service_code = models.CharField(null=True, max_length=120)
    service_name = models.TextField(blank=True, default="")
    description = models.TextField(blank=True, default="")
    agency_responsible = models.TextField(blank=True, default="")
    service_notice = models.TextField(blank=True, default="")
    requested_datetime = models.DateTimeField(null=True, default=timezone.now)
    updated_datetime = models.DateTimeField(null=True)
    expected_datetime = models.DateTimeField(null=True)
    address_string = models.TextField(blank=True, default="")
    media_url = models.URLField(blank=True, default="")

    email = models.TextField(blank=True, default="")
    first_name = models.TextField(blank=True, default="")
    last_name = models.TextField(blank=True, default="")
    phone = models.TextField(blank=True, default="")

    # extended attributes
    service_object_id = models.TextField(blank=True, default="")
    title = models.TextField(blank=True, default="")
    service_object_type = models.TextField(blank=True, default="")
    detailed_status = models.TextField(blank=True, default="")

    location = models.PointField(srid=4326, null=True)

    # Keeps track of votes users have given to the issue
    vote_counter = models.IntegerField(default=0)

    # synchronized with external Open311 service
    synchronized = models.BooleanField(default=False)

    @property
    def lon(self):
        return self.location[0]

    @property
    def lat(self):
        return self.location[1]

    def save(self, **kwargs):
        self._cache_data()
        super(Issue, self).save(**kwargs)

    def _generate_service_request_id(self):
        for length in range(8, 65, 4):
            for attempt in range(10):
                id = get_random_string(length, allowed_chars=ID_KEYSPACE)
                if not Issue.objects.filter(service_request_id=id).exists():
                    # There's a minuscule chance of a race condition here, but the worst case
                    # is that the transaction fails and the client needs to try again.
                    return id

    def _cache_data(self):
        if not self.jurisdiction_id:
            self.jurisdiction = Jurisdiction.autodetermine()
        if not self.service_request_id:
            self.service_request_id = self._generate_service_request_id()
        if not self.service_id:
            self.service, created = Service.objects.get_or_create(service_code=self.service_code, defaults={
                "service_name": self.service_code
            })
        if not self.service_name:
            self.service_name = self.service.service_name
        if not self.service_code:
            self.service_code = self.service.service_code


class MediaURL(models.Model):
    issue = models.ForeignKey('Issue', on_delete=models.CASCADE, related_name='media_urls', null=True)
    media_url = models.URLField()


class Task(models.Model):
    issue = models.ForeignKey('Issue', on_delete=models.CASCADE, related_name='tasks', null=True)
    task_state = models.TextField(blank=True, default="")
    task_type = models.TextField(blank=True, default="")
    owner_name = models.TextField(blank=True, default="")
    task_modified = models.DateTimeField(null=True)
    task_created = models.DateTimeField(null=True)


class Service(models.Model):
    service_code = models.CharField(unique=True, null=False, max_length=120)
    service_name = models.TextField(blank=False)
    description = models.TextField(blank=True, default="")
    metadata = models.BooleanField(default=False)
    type = models.TextField(max_length=140, default="other")
    keywords = models.TextField(blank=True, default="")
    group = models.CharField(max_length=140, blank=True, default="")  # The choices are "realtime", "batch" and "blackbox" according to the GeoReport spec
    jurisdictions = models.ManyToManyField("Jurisdiction", related_name="services")


# Uploaded temporary media files binded to form instance
# Delete MediaFile objects+files when they are old
# Delete MediaFile objects and leave files when files
# are binded to Issue
# Default directory is MEDIA_ROOT
class MediaFile(models.Model):
    issue = models.ForeignKey('Issue', on_delete=models.CASCADE, related_name="media_files", null=True)
    file = models.FileField()
    original_filename = models.CharField(max_length=255, blank=True)
    form_id = models.CharField(max_length=50)
    date_created = models.DateTimeField(auto_now_add=True)
    size = models.IntegerField(default=0)
