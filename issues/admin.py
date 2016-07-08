from django.contrib.admin import site, ModelAdmin
from parler.admin import TranslatableAdmin

from .models import Issue, Jurisdiction, Service, Application


class ApplicationAdmin(ModelAdmin):
    list_display = ('identifier', 'name', 'active')
    list_filter = ('active',)
    search_fields = ('identifier', 'name',)

    def get_readonly_fields(self, request, obj=None):
        fields = super().get_readonly_fields(request, obj)
        if obj and obj.pk:
            fields += ('key',)
        return fields


class ServiceAdmin(TranslatableAdmin):
    list_display = ('service_code', 'service_name')
    search_fields = ('translations__service_name',)


site.register((Issue, Jurisdiction))
site.register(Service, ServiceAdmin)
site.register(Application, ApplicationAdmin)
