import json

from django import template
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.middleware.csrf import get_token
from django.utils.safestring import mark_safe
from django.utils.translation import get_language

from issues.excs import InvalidAppError
from issues.models import Application
from issues_simple_ui.models import Content, Image

register = template.Library()


@register.simple_tag
def get_content(identifier):
    return Content.retrieve(identifier)


@register.simple_tag
def get_image(identifier):
    try:
        return Image.objects.get(identifier=identifier).file.url
    except ObjectDoesNotExist:
        return None


@register.simple_tag(takes_context=True)
def get_config_json(context, **extra):
    """
    Get a JSON blob that is used to configure the frontend JavaScript.

    :param context: Django rendering context
    :param extra: Extra attributes to inject
    :return:
    """
    request = context['request']
    user = request.user
    if user and user.is_authenticated():
        extra['csrf_token'] = get_token(request)

    try:
        application = Application.autodetermine()
    except InvalidAppError:
        application, _ = Application.objects.get_or_create(
            identifier='simple_ui',
            defaults={'name': 'Simple UI',},
        )

    return mark_safe(json.dumps(dict({
        'language': get_language().split('-')[0],
        'api_key': application.key,
        'api_root': '/%s' % settings.GEOREPORT_API_ROOT,
        'map_settings': {  # TODO: Make this configurable
            'center': [60.1699, 24.9384],
            'tileUrl': 'http://otile1.mqcdn.com/tiles/1.0.0/map/{z}/{x}/{y}.png',
            'attribution': 'Tiles Courtesy of <a href="http://www.mapquest.com/" target="_blank">MapQuest</a>',
        },
    }, **extra)))
