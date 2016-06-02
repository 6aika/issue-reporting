from django.utils.encoding import force_text


def parse_bbox(bbox):
    """
    Parse a bounding box string into an lat/lon/lat/long 4-tuple.

    :param bbox: bounding box string
    :return: pair of coordinates
    :rtype: tuple[tuple[float, float], tuple[float, float]]
    """
    bbox = force_text(bbox)
    sep = (';' if ';' in bbox else ',')
    try:
        lat1, lon1, lat2, lon2 = [float(c) for c in bbox.split(sep)]
    except IndexError:
        raise ValueError('bbox %r is not exactly 4 coordinates' % bbox)
    except ValueError as exc:
        raise ValueError('bbox %r has invalidly formed numbers (%s)' % (bbox, exc))
    if lat1 > lat2:
        lat2, lat1 = lat1, lat2
    if lon1 > lon2:
        lon2, lon1 = lon1, lon2

    for lat in (lat1, lat2):
        if not (-90 < lat < +90):
            raise ValueError('latitude %f is out of range (-90..+90)' % lat)

    for lon in (lon1, lon2):
        if not (-180 < lon < +180):
            raise ValueError('longitude %f is out of range (-180..+180)' % lon)

    return ((lat1, lon1), (lat2, lon2))
