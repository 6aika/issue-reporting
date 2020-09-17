import pytest
from django.core.urlresolvers import reverse_lazy
from django.utils.crypto import get_random_string

from issues.models import Jurisdiction
from issues.models.services import Service
from issues.tests.utils import get_data_from_response

TEST_LOCALES = ("en", "fi", "sv")

SERVICE_LIST_ENDPOINT = reverse_lazy('georeport/v2:service-list')


def test_service_list_i18n(mf_api_client, random_service):
    assert isinstance(random_service, Service)
    for lang in TEST_LOCALES:
        random_service.set_current_language(lang)
        random_service.service_name = f"Test-{lang}"
    random_service.save_translations()
    for lang in TEST_LOCALES:
        data = get_data_from_response(
            mf_api_client.get(
                SERVICE_LIST_ENDPOINT,
                {"locale": lang}
            )
        )
        assert len(data) == 1
        assert data[0]['service_name'].endswith(lang)  # As we set above


@pytest.mark.django_db
def test_service_list_jurisdiction_filter(mf_api_client):
    tku = Jurisdiction.objects.create(identifier='fi.turku')
    hel = Jurisdiction.objects.create(identifier='fi.hel')
    tku_service = Service.objects.create(service_code=get_random_string(), service_name='Aurajokipalvelu')
    hel_service = Service.objects.create(service_code=get_random_string(), service_name='Suomenlinnapalvelu')
    tku_service.jurisdictions.add(tku)
    hel_service.jurisdictions.add(hel)
    for query, expected in (
        ({}, [tku_service, hel_service]),
        ({'jurisdiction_id': tku.identifier}, [tku_service]),
        ({'jurisdiction_id': hel.identifier}, [hel_service]),
    ):
        data = get_data_from_response(
            mf_api_client.get(SERVICE_LIST_ENDPOINT, query)
        )
        assert len(data) == len(expected)
        assert {s['service_name'] for s in data} == {s.service_name for s in expected}
