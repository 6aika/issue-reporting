import pytest
from django.contrib.gis.db.models.fields import GeometryField
from django.contrib.gis.geos import GEOSGeometry
from django.db import models, connection
from django.db.models import Field
from django.db.models.sql import InsertQuery, Query
from django.db.models.sql.compiler import SQLInsertCompiler, SQLCompiler

from issues.fields import FallbackPointField, _FallbackPointField
from issues.gis import determine_gissiness


class TotesAModel(models.Model):
    f = _FallbackPointField()

    class Meta:
        db_table = 'foo'
        managed = False


def test_fallbackpointfield_heritage():
    assert issubclass(FallbackPointField, Field)  # Well that's a given.
    assert issubclass(FallbackPointField, GeometryField) == determine_gissiness()  # Only geometrical if gissy!


@pytest.mark.parametrize('val', [
    (60, 22),
    GEOSGeometry('SRID=4326;POINT(60 22)'),
    '60;22'
])
def test_fallback_serialization(val):
    """
    Test that the non-gissy fallback point field does actually serialize into a semicolon-separated
    format even in the SQL level.
    """
    obj = TotesAModel(f=val)
    query = InsertQuery(TotesAModel)
    query.insert_values(TotesAModel._meta.get_fields(), [obj])
    comp = query.get_compiler(using="default")
    assert isinstance(comp, SQLInsertCompiler)
    comp.return_id = True  # prevent bulk
    sql, params = comp.as_sql()[0]
    assert "60.0;22.0" in params


@pytest.mark.parametrize('val', [
    "60;22",
    "60.0;22.0",
])
def test_fallback_deserialization(val):
    """
    Test that semicola-separated values from the database get deserialized into 2-tuples.
    """
    field = [f for f in TotesAModel._meta.get_fields() if isinstance(f, _FallbackPointField)][0]
    assert field.to_python(val) == (60, 22)
