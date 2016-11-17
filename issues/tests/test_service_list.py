from django.core.urlresolvers import reverse_lazy

from issues.models.services import Service
from issues.tests.utils import get_data_from_response

TEST_LOCALES = ("en", "fi", "sv")

SERVICE_LIST_ENDPOINT = reverse_lazy('georeport/v2:service-list')


def test_service_list_i18n(mf_api_client, random_service):
    assert isinstance(random_service, Service)
    for lang in TEST_LOCALES:
        random_service.set_current_language(lang)
        random_service.service_name = "Test-%s" % lang
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
