from rest_framework import serializers

from .models import Feedback, Task


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
        }

        extensions = self.context.get('extensions')
        if extensions and extensions[0].upper() == 'T':
            ext_attribute = self.fields['extended_attributes']
            ext_attribute_value = ext_attribute.to_representation(
                    ext_attribute.get_attribute(instance)
            )
            representation['extended_attributes'] = ext_attribute_value

        return representation
