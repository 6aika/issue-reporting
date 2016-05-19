from django.contrib.gis.db import models
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _

LOG_STATUS_CHOICES = [
    # Request has been allocated to handler, can happen several times:
    ('allocated', _('allocated')),

    # Request is being handled (ie. request has been handed off to someone
    # who will fix the broken things or answer information request):
    ('handling', _('handling')),

    # Request has been handled and something has been done to handle it:
    ('done', _('done')),
]


class LogEntry(models.Model):
    issue = models.ForeignKey('issues.Issue', on_delete=models.CASCADE, related_name='log_entries')
    time = models.DateTimeField(default=now, db_index=True)
    status = models.CharField(max_length=32, choices=LOG_STATUS_CHOICES)
    note = models.TextField(blank=True)
    handler = models.CharField(blank=True, max_length=128)
    attachment_url = models.URLField(blank=True)

    class Meta:
        ordering = ('time',)


class Issue_LogExtension(models.Model):
    issue = models.OneToOneField('issues.Issue', on_delete=models.CASCADE, related_name='log_ext')
    last_handler = models.CharField(blank=True, max_length=128, editable=False)

    class Meta:
        verbose_name = 'issue log extension'
        verbose_name_plural = 'issue log extensions'
        db_table = 'issues_log_extension'
