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
    jurisdiction_id = serializers.SlugRelatedField(
        queryset=Jurisdiction.objects.all(),
        source='jurisdiction',
        required=False,
        slug_field='identifier',
        write_only=True,
    )
    lat = serializers.FloatField(required=False)
    long = serializers.FloatField(required=False)
    address = serializers.CharField(required=False, source="address_string", read_only=True)

    class Meta:
        model = Issue
        fields = [
            'address',
            'agency_responsible',
            'description',
            'expected_datetime',
            'extended_attributes',
            'distance',
            'jurisdiction_id',
            'lat',
            'long',
            'media_url',
            'requested_datetime',
            'service_code',
            'service_name',
            'service_notice',
            'service_request_id',
            'status',
            'status_notes',
            'updated_datetime',
        ]
        read_only_fields = [
            'service_request_id',
            'service_name',
        ]
        write_only_fields = [  # This is not directly supported by DRF; see below for the patch
            'address_string',
            'first_name',
            'last_name',
            'email',
            'phone',
        ]
        extra_kwargs = {
            'service_code': {'required': True}
        }
        for f in write_only_fields:
            extra_kwargs.setdefault(f, {})["write_only"] = True

    def get_distance(self, obj):
        if hasattr(obj, 'distance'):
            return float(obj.distance.m)
        else:
            return None

    def get_extended_attributes(self, instance):
        if not self.context.get('extensions'):
            return None

        media_urls_value = sorted(instance.media_urls.values_list('media_url'))

        tasks = TaskSerializer(many=True, read_only=True)
        tasks.source_attrs = ["tasks"]
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

        if representation.get('extended_attributes') is None:
            representation.pop('extended_attributes', None)

        if representation.get('distance') is None:
            representation.pop('distance')

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
