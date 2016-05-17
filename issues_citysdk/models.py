from django.db import models


class Issue_CitySDK(models.Model):
    issue = models.OneToOneField('issues.Issue', related_name="citysdk")
    service_object_id = models.CharField(max_length=100, blank=True)
    service_object_type = models.CharField(max_length=100, blank=True)
    title = models.CharField(max_length=120, blank=True)
    detailed_status = models.TextField(blank=True)

    class Meta:
        verbose_name = 'issue CitySDK extension'
        verbose_name_plural = 'issue CitySDK extensions'
        db_table = 'issue_citysdk_ext'
