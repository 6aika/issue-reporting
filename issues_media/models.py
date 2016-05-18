from django.db import models


# TODO: what to do about file size/mimetype limitations?

class IssueMedia(models.Model):
    issue = models.ForeignKey('issues.Issue', related_name='media')
    file = models.FileField(upload_to='i/%Y/%Y%m/%Y%m%d')
