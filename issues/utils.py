from django.utils.encoding import force_str


def parse_bbox(bbox):
    """
    Parse a bounding box string into an lon/lat/lon/lat 4-tuple.

    :param bbox: bounding box string
    :return: pair of coordinates
    :rtype: tuple[tuple[float, float], tuple[float, float]]
    """
    bbox = force_str(bbox)
    sep = (';' if ';' in bbox else ',')
    try:
        lon1, lat1, lon2, lat2 = [float(c) for c in bbox.split(sep)]
    except IndexError:
        raise ValueError(f'bbox {bbox!r} is not exactly 4 coordinates')
    except ValueError as exc:
        raise ValueError(f'bbox {bbox!r} has invalidly formed numbers ({exc})')
    if lat1 > lat2:
        lat2, lat1 = lat1, lat2
    if lon1 > lon2:
        lon2, lon1 = lon1, lon2

    for lat in (lat1, lat2):
        if not (-90 < lat < +90):
            raise ValueError(f'latitude {lat:f} is out of range (-90..+90)')

    for lon in (lon1, lon2):
        if not (-180 < lon < +180):
            raise ValueError(f'longitude {lon:f} is out of range (-180..+180)')

    return ((lon1, lat1), (lon2, lat2))
