from django.conf import settings
from django.contrib.gis.geos import GEOSGeometry
from rest_framework import serializers
from rest_framework.fields import empty
from rest_framework.utils import model_meta

from issues.api.utils import XMLDict
from issues.excs import MultipleJurisdictionsError
from issues.extensions import get_extensions
from issues.models import Issue, Jurisdiction, Service


class ServiceSerializer(serializers.ModelSerializer):

    class Meta:
        model = Service
        fields = ['service_code', 'service_name', 'description', 'metadata', 'type', 'keywords', 'group']


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
    service_name = serializers.SerializerMethodField(read_only=True)
    service_request_id = serializers.CharField(read_only=True, source='identifier')

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
        write_only_fields = [  # This is not directly supported by DRF; see below for the patch
            'address_string',
            'first_name',
            'last_name',
            'email',
            'phone',
        ]
        extra_kwargs = {
            'service_code': {'required': True},
        }
        for f in write_only_fields:
            extra_kwargs.setdefault(f, {})["write_only"] = True

    def __init__(self, instance=None, data=empty, **kwargs):
        super().__init__(instance, data, **kwargs)

        for ext in self.context.get('extensions', ()):
            ext.extend_issue_serializer(self)

    def get_distance(self, obj):
        if hasattr(obj, 'distance'):
            return float(obj.distance.m)
        else:
            return None

    def get_service_name(self, obj):
        return obj.service.safe_translation_getter(
            "service_name",
            default=obj.service.service_code,
            any_language=True
        )

    def get_extended_attributes(self, obj):
        extensions = self.context.get('extensions', ())
        extended_attributes = {}
        for ex in extensions:
            extended_attributes.update(
                ex.get_extended_attributes(
                    issue=obj,
                    context=self.context
                ) or {}
            )
        return extended_attributes

    def to_representation(self, instance):
        """

        :type instance: issues.models.Issue
        :rtype: dict
        """
        representation = super(IssueSerializer, self).to_representation(instance)
        if not (instance.lat and instance.long):  # Remove null coordinate fields
            representation.pop('lat', None)
            representation.pop('long', None)

        if not self.context.get('extensions', ()):
            representation.pop('extended_attributes', None)

        if representation.get('distance') is None:
            representation.pop('distance')

        return XMLDict(representation, "request")

    def validate(self, data):
        service_code = data.pop('service_code')
        service = Service.objects.filter(service_code=service_code).first()
        if not service:
            raise serializers.ValidationError('Service code %s is invalid' % service_code)
        data['service'] = service

        lat = data.pop('lat', None)
        long = data.pop('long', None)
        if lat and long:
            data['location'] = GEOSGeometry(  # TODO: Maybe remove? Looks like a GEOS dependency
                'SRID=4326;POINT(%s %s)' % (long, lat)
            )

        if not data.get('jurisdiction'):
            try:
                data['jurisdiction'] = Jurisdiction.autodetermine()
            except MultipleJurisdictionsError as mjd:
                raise serializers.ValidationError(mjd.args[0])

        for ex in self.context.get('extensions', ()):
            new_data = ex.validate_issue_data(self, data)
            if new_data:
                data = new_data

        return data

    def create(self, validated_data):
        validated_data['moderation'] = getattr(settings, 'ISSUES_DEFAULT_MODERATION_STATUS', 'public')
        instance = self._create(validated_data)
        extensions = get_extensions()
        request = self.context['request']
        for ex in extensions:
            ex().post_create_issue(request=request, issue=instance, data=validated_data)
        return instance

    def _create(self, validated_data):
        validated_data = validated_data.copy()  # We're going to pop stuff off here.
        # This logic is mostly copied from super().create(),
        # aside from the concrete_data stuff.
        ModelClass = self.Meta.model
        info = model_meta.get_field_info(ModelClass)
        many_to_many = {}
        for field_name, relation_info in info.relations.items():
            if relation_info.to_many and (field_name in validated_data):
                many_to_many[field_name] = validated_data.pop(field_name)

        # Build a dict of fields we're guaranteed to be able to pass to `Model.create()`
        concrete_fields = set(info.fields) | set(info.forward_relations)
        concrete_data = {
            field: value
            for (field, value)
            in validated_data.items()
            if field in concrete_fields
        }
        instance = ModelClass.objects.create(**concrete_data)
        for field_name, value in many_to_many.items():
            setattr(instance, field_name, value)
        return instance
