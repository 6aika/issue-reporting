from rest_framework import serializers

from issues.api.utils import XMLDict
from issues_hel.models import Task


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['task_state', 'task_type', 'owner_name', 'task_modified', 'task_created']

    def to_representation(self, instance):
        return XMLDict(
            super().to_representation(instance),
            'task'
        )
