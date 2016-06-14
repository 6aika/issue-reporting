from django.contrib.admin import site, ModelAdmin

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


site.register((Issue, Jurisdiction, Service))
site.register(Application, ApplicationAdmin)
