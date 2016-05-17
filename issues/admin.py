from django.contrib.admin import site
from .models import Issue, Jurisdiction, Service

site.register((Issue, Jurisdiction, Service))
