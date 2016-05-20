from django.contrib.gis.db import models
from django.utils.six import python_2_unicode_compatible

from issues.excs import MultipleJurisdictionsError


@python_2_unicode_compatible
class Jurisdiction(models.Model):
    identifier = models.CharField(max_length=64, unique=True)
    name = models.CharField(max_length=64)

    @staticmethod
    def autodetermine():
        jurisdiction_count = Jurisdiction.objects.count()
        if jurisdiction_count == 0:
            return Jurisdiction.objects.create(
                identifier="default",
                name="Default"
            )
        elif jurisdiction_count == 1:
            return Jurisdiction.objects.first()
        raise MultipleJurisdictionsError("Jurisdiction must be chosen (there are %d)" % jurisdiction_count)

    def __str__(self):
        return self.name
