from django.contrib import admin
from django.forms.widgets import RadioSelect
from parler.admin import TranslatableAdmin

from issues_simple_ui.enums import CONTENT_IDENTIFIERS, IMAGE_IDENTIFIERS
from issues_simple_ui.models import Content, Image


class ContentAdmin(TranslatableAdmin):
    list_display = ('identifier', 'all_languages_column')

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['identifier'].widget = RadioSelect(choices=CONTENT_IDENTIFIERS)
        return form


class ImageAdmin(admin.ModelAdmin):
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['identifier'].widget = RadioSelect(choices=IMAGE_IDENTIFIERS)
        return form


admin.site.register(Content, ContentAdmin)
admin.site.register(Image, ImageAdmin)
