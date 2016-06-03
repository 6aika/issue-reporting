from django.contrib import admin
from parler.admin import TranslatableAdmin

from issues_simple_ui.models import Content, Image

admin.site.register(Content, TranslatableAdmin)
admin.site.register(Image)
