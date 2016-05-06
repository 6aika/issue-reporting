from django.contrib.gis.geos import GEOSGeometry
from rest_framework import serializers

from issues.models import Issue, Service, Task, Jurisdiction, MultipleJurisdictionsError


class ServiceSerializer(serializers.ModelSerializer):

    class Meta:
        model = Service
        fields = ['service_code', 'service_name', 'description', 'metadata', 'type', 'keywords', 'group']


class TaskSerializer(serializers.ModelSerializer):

    class Meta:
        model = Task
        fields = ['task_state', 'task_type', 'owner_name', 'task_modified', 'task_created']


class IssueSerializer(serializers.ModelSerializer):
    distance = serializers.SerializerMethodField()
    extended_attributes = serializers.SerializerMethodField()
    media_urls = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field='media_url',
    )
    tasks = TaskSerializer(many=True, read_only=True)
    jurisdiction_id = serializers.SlugRelatedField(
        queryset=Jurisdiction.objects.all(),
        source='jurisdiction',
        required=False,
        slug_field='identifier',
        write_only=True,
    )
    lat = serializers.FloatField(required=False)
    long = serializers.FloatField(required=False)

    class Meta:
        model = Issue
        exclude = [
            'jurisdiction',  # Manually defined as `jurisdiction_id`
            'service',  # Determined via `service_code`
        ]
        read_only_fields = [
            'service_request_id',
            'service_name',
        ]
        extra_kwargs = {
            'service_code': {'required': True}
        }

    def get_distance(self, obj):
        if hasattr(obj, 'distance'):
            return float(obj.distance.m)
        else:
            return ''

    def get_extended_attributes(self, instance):
        if not self.context.get('extensions'):
            return None

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
            'vote_counter': instance.vote_counter,
            'media_urls': media_urls_value,
            'tasks': tasks_value
        }

        return representation

    def to_representation(self, instance):
        """

        :type instance: issues.models.Issue
        :return:
        """
        representation = super(IssueSerializer, self).to_representation(instance)
        if representation.get("lat") is None:  # No location? Don't emit it.
            representation.pop("lat", None)
            representation.pop("long", None)

        # TODO: title, vote_counter
        if representation.get('extended_attributes') is None:
            representation.pop('extended_attributes', None)

        return representation

    def validate(self, data):
        service_code = data.pop('service_code')
        service = Service.objects.filter(service_code=service_code).first()
        if not service:
            raise serializers.ValidationError('Service code %s is invalid' % service_code)
        data['service'] = service

        lat = data.get('lat')
        long = data.get('long')
        service_object_id = data.get('service_object_id')
        if (lat is None or long is None) and service_object_id is None:
            raise serializers.ValidationError('Currently all service types require location, '
                                              'either lat/long or service_object_id.')
        data['location'] = GEOSGeometry(
            'SRID=4326;POINT(%s %s)' % (
                data.pop('long', 0),
                data.pop('lat', 0)
            )
        )

        if not data.get('jurisdiction'):
            try:
                data['jurisdiction'] = Jurisdiction.autodetermine()
            except MultipleJurisdictionsError as mjd:
                raise serializers.ValidationError(mjd.args[0])

        return data
