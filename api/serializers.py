from rest_framework import serializers

from .models import Feedback


class FeedbackSerializer(serializers.ModelSerializer):
    distance = serializers.SerializerMethodField()

    def get_distance(self, obj):
        return obj.distance.m

    class Meta:
        model = Feedback
        fields = ('id', 'distance', 'service_request_id', 'address_string', 'service_code')
