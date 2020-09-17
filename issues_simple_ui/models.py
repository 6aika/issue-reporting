from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.utils.translation import gettext_lazy as _
from parler.models import TranslatableModel, TranslatedFields


class Content(TranslatableModel):
    identifier = models.CharField(
        max_length=64,
        unique=True,
        db_index=True,
        help_text=_('an identifier used by the system to place this content'),
    )

    translations = TranslatedFields(
        title=models.CharField(max_length=120, blank=True),
        content=models.TextField(blank=True),
    )

    @classmethod
    def retrieve(cls, identifier):
        try:
            obj = cls.objects.get(identifier=identifier)
            return {
                'title': obj.safe_translation_getter('title'),
                'content': obj.safe_translation_getter('content'),
            }
        except ObjectDoesNotExist:
            return {}

    def __str__(self):
        return self.identifier


class Image(models.Model):
    identifier = models.CharField(
        max_length=64,
        unique=True,
        db_index=True,
        help_text=_('an identifier used by the system to place this image'),
    )

    file = models.FileField(upload_to="ui/img")  # This could be an ImageField, but that adds a Pillow dependency

    def __str__(self):
        return self.identifier
