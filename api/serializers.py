from datetime import timedelta, datetime

from django.conf import settings
from django.contrib.gis.geos import GEOSGeometry
from rest_framework import serializers

from api.analysis import calc_fixing_time
from .models import Feedback, Task, Service


class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = ['service_code', 'service_name', 'description', 'metadata', 'type', 'keywords', 'group']


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['task_state', 'task_type', 'owner_name', 'task_modified', 'task_created']


class FeedbackSerializer(serializers.ModelSerializer):
    distance = serializers.SerializerMethodField()
    extended_attributes = serializers.SerializerMethodField()
    media_urls = serializers.SlugRelatedField(
            many=True,
            read_only=True,
            slug_field='media_url'
    )
    tasks = TaskSerializer(many=True)

    class Meta:
        model = Feedback

    def get_distance(self, obj):
        if hasattr(obj, 'distance'):
            return int(obj.distance.m)
        else:
            return ''

    def get_extended_attributes(self, instance):

        media_urls = self.fields['media_urls']
        media_urls_value = media_urls.to_representation(
                media_urls.get_attribute(instance)
        )

        tasks = self.fields['tasks']
        tasks_value = tasks.to_representation(
                tasks.get_attribute(instance)
        )

        representation = {
            'service_object_type': instance.service_object_type,
            'service_object_id': instance.service_object_id,
            'detailed_status': instance.detailed_status,
            'title': instance.title,
            'media_urls': media_urls_value,
            'tasks': tasks_value
        }

        return representation

    def to_representation(self, instance):
        distance = self.fields['distance']
        distance_value = distance.to_representation(
                distance.get_attribute(instance)
        )

        representation = {
            'id': instance.id,
            'distance': distance_value,
            'service_request_id': instance.service_request_id,
            'status_notes': instance.status_notes,
            'status': instance.status,
            'service_code': instance.service_code,
            'service_name': instance.service_name,
            'description': instance.description,
            'agency_responsible': instance.agency_responsible,
            'service_notice': instance.service_notice,
            'requested_datetime': instance.requested_datetime,
            'updated_datetime': instance.updated_datetime,
            'expected_datetime': instance.expected_datetime,
            'address': instance.address_string,
            'lat': instance.lat,
            'long': instance.lon,
            'media_url': instance.media_url,
            'vote_counter': instance.vote_counter,
            'title': instance.title
        }

        extensions = self.context.get('extensions')
        if extensions and extensions[0].upper() == 'T':
            ext_attribute = self.fields['extended_attributes']
            ext_attribute_value = ext_attribute.to_representation(
                    ext_attribute.get_attribute(instance)
            )
            representation['extended_attributes'] = ext_attribute_value

        return representation


class FeedbackDetailSerializer(serializers.ModelSerializer):
    api_key = serializers.CharField(required=True)
    service_code = serializers.IntegerField(required=True)
    description = serializers.CharField(required=True, min_length=10, max_length=5000)
    title = serializers.CharField(required=False)
    lat = serializers.FloatField(required=False)
    long = serializers.FloatField(required=False)
    service_object_type = serializers.CharField(required=False)
    service_object_id = serializers.CharField(required=False)
    address_string = serializers.CharField(required=False)
    email = serializers.CharField(required=False)
    first_name = serializers.CharField(required=False)
    last_name = serializers.CharField(required=False)
    phone = serializers.CharField(required=False)
    media_url = serializers.CharField(required=False)

    def validate(self, data):
        """
        Check location fields.
        """
        lat = data.get('lat')
        long = data.get('long')
        service_object_id = data.get('service_object_id')
        if (lat is None or long is None) and service_object_id is None:
            raise serializers.ValidationError("Currently all service types require location, "
                                              "either lat/long or service_object_id.")
        return data

    def create(self, validated_data):
        location = GEOSGeometry(
            'SRID=4326;POINT(' + str(validated_data.get('long', 0)) + ' ' + str(validated_data.get('lat', 0)) + ')')
        validated_data['location'] = location

        fixing_time = calc_fixing_time(validated_data["service_code"])
        waiting_time = timedelta(milliseconds=fixing_time)

        if waiting_time.total_seconds() >= 0:
            validated_data['expected_datetime'] = datetime.now() + waiting_time

        if settings.SYNCHRONIZE_WITH_OPEN_311 is False:
            validated_data['service_request_id'] = Feedback.generate_service_request_id()
            validated_data['status'] = 'moderation'

        validated_data.pop('lat', None)
        validated_data.pop('long', None)
        feedback = Feedback.objects.create(**validated_data)
        feedback = Feedback.objects.get(pk=feedback.pk)
        return feedback

    class Meta:
        model = Feedback
