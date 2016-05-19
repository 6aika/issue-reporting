from django.contrib.gis.db import models


class Task(models.Model):
    issue = models.ForeignKey('issues.Issue', on_delete=models.CASCADE, related_name='tasks')
    task_state = models.TextField(blank=True)
    task_type = models.TextField(blank=True)
    owner_name = models.TextField(blank=True)
    task_modified = models.DateTimeField(null=True)
    task_created = models.DateTimeField(db_index=True)

    class Meta:
        ordering = ('task_created', )
