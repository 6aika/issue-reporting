from django.contrib.gis.db import models
from django.utils import timezone

# TODO: change some TextFields with CharFields, remove null=True where required
class Feedback(models.Model):
    class Meta:
        db_table = 'feedbacks'

    service_request_id = models.CharField(max_length=254, db_index=True, unique=False)
    status_notes = models.TextField(null=True)
    status = models.TextField(null=True)
    service_code = models.TextField(null=True)
    service_name = models.TextField(null=True)
    description = models.TextField(null=True)
    agency_responsible = models.TextField(null=True)
    service_notice = models.TextField(null=True)
    requested_datetime = models.DateTimeField(null=True, default=timezone.now)
    updated_datetime = models.DateTimeField(null=True)
    expected_datetime = models.DateTimeField(null=True)
    address_string = models.TextField(null=True)
    media_url = models.TextField(null=True)

    api_key = models.TextField(null=True)
    email = models.TextField(null=True)
    first_name = models.TextField(null=True)
    last_name = models.TextField(null=True)
    phone = models.TextField(null=True)

    # extended attributes
    service_object_id = models.TextField(null=True)
    title = models.TextField(null=True)
    service_object_type = models.TextField(null=True)
    detailed_status = models.TextField(null=True)

    location = models.PointField(srid=4326)

    # Keeps track of votes users have given to the feedback
    vote_counter = models.IntegerField(default=0)

    @property
    def lon(self):
        return self.location[0]

    @property
    def lat(self):
        return self.location[1]


class MediaURL(models.Model):
    class Meta:
        db_table = 'media_urls'

    feedback = models.ForeignKey('Feedback', on_delete=models.CASCADE, related_name='media_urls', null=True)
    media_url = models.TextField(null=True)


class Task(models.Model):
    class Meta:
        db_table = 'tasks'

    feedback = models.ForeignKey('Feedback', on_delete=models.CASCADE, related_name='tasks', null=True)
    task_state = models.TextField(null=True)
    task_type = models.TextField(null=True)
    owner_name = models.TextField(null=True)
    task_modified = models.DateTimeField(null=True)
    task_created = models.DateTimeField(null=True)
