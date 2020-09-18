import json

from django.urls import reverse
from rest_framework.test import APIClient


class APIClientWrapper(APIClient):

    def get(self, path, data=None, follow=False, **extra):
        response = super().get(reverse(path), data, follow)
        content = json.loads(response.content.decode('utf-8'))
        return response, content
