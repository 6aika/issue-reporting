import json
import logging
import urllib
from urllib.error import URLError

from django.conf import settings
from geopy.geocoders import Nominatim

logger = logging.getLogger(__name__)


def reverse_geocode(lat, lon):
    if settings.USE_NOMINATIM:
        return reverse_geocode_nominatim(lat, lon)
    else:
        return reverse_geocode_servicemap(lat, lon)


def reverse_geocode_nominatim(lat, lon):
    geolocator = Nominatim()
    location = geolocator.reverse("{}, {}".format(lat, lon))
    logger.info('found address: ' + location.address)
    return location.address


def reverse_geocode_servicemap(lat, lon):
    reverse_geocoding_url = settings.REVERSE_GEO_URL.format(lat, lon)
    logger.info('url to send: {}'.format(reverse_geocoding_url))

    try:
        response = urllib.request.urlopen(reverse_geocoding_url)
        content = response.read()
        json_data = json.loads(content.decode("utf8"))
    except ValueError:
        logger.exception('Decoding JSON has failed')
        return
    except URLError:
        logger.exception('Invalid URL: {}'.format(reverse_geocoding_url))
        return
    pass

    results_json = json_data.get('results', None)
    if results_json:
        res = results_json[0]
        street = res['street']['name']['fi'] + ' ' + res['number']
        municipality = res['street']['municipality'].capitalize()
        address_string = street + ', ' + municipality
        logger.info('found address: ' + address_string)
        return address_string

    logger.info('address not found')
    return ''
