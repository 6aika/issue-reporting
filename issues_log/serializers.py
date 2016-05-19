from rest_framework import serializers

from issues.api.utils import XMLDict
from issues_log.models import LogEntry


class LogEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = LogEntry
        exclude = ('issue',)

    def to_representation(self, instance):
        return XMLDict(super().to_representation(instance), 'entry')
