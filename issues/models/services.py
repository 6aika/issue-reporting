from django.contrib.gis.db import models
from django.utils.translation import gettext_lazy as _
from parler.models import TranslatableModel, TranslatedFields


class Service(TranslatableModel):
    jurisdictions = models.ManyToManyField("Jurisdiction", related_name="services")
    service_code = models.CharField(unique=True, null=False, max_length=120)
    metadata = models.BooleanField(default=False)
    type = models.CharField(
        max_length=140,
        default="realtime",
        choices=[
            ("realtime", _("Realtime")),
            ("batch", _("Batch")),
            ("blackbox", _("Black Box")),
        ]
    )
    location_req = models.CharField(
        verbose_name=_("location requirement"),
        max_length=32,
        default="coords_or_address",
        choices=[
            ("coords_or_address", _("require coordinates or address")),
            ("coords", _("require coordinates (no address)")),
            ("none", _("require no location")),
        ],
    )

    translations = TranslatedFields(
        service_name=models.CharField(max_length=120, blank=False),
        description=models.TextField(blank=True),
        keywords=models.TextField(blank=True),
        group=models.CharField(max_length=140, blank=True, default="")
    )

    def __str__(self):
        return self.safe_translation_getter("service_name", default=self.service_code)
