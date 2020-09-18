from warnings import warn

from django.contrib.gis.db.backends.base.operations import BaseSpatialOperations
from django.db import connections, DEFAULT_DB_ALIAS


class NoIssueGIS(Warning):
    pass


def determine_gissiness():
    try:
        from django.contrib.gis.db.models.fields import PointField
    except ImportError:  # pragma: no cover
        warn(
            "Could not import the PointField class; Issue GIS features are not enabled.",
            NoIssueGIS
        )
        return False

    connection = connections[DEFAULT_DB_ALIAS]

    if not isinstance(connection.ops, BaseSpatialOperations):  # pragma: no cover
        warn(
            f"The default connection {connection!r} is not GIS-enabled; Issue GIS features are not enabled.",
            NoIssueGIS
        )
        return False

    return True
