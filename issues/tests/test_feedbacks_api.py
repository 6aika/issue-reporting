from rest_framework import status
from rest_framework.test import APITestCase

from issues.tests.api_utils import APIClientWrapper
from issues.tests.db_utils import clear_db, insert_feedbacks


class RequestsAPITest(APITestCase):
    # request constants
    NUMBER_OF_REQUESTS = 4

    @classmethod
    def setUpClass(cls):
        clear_db()
        insert_feedbacks()

    @classmethod
    def tearDownClass(cls):
        clear_db()

    def setUp(self):
        self.client = APIClientWrapper()

    def test_get_requests(self):
        response, content = self.client.get('api/v1:feedback-list')
        self.assertTrue(response.status_code == status.HTTP_200_OK)
        self.assertTrue(len(content) == RequestsAPITest.NUMBER_OF_REQUESTS)

    def test_get_by_service_request_id(self):
        response, content = self.client.get('api/v1:feedback-list', {'service_request_id': '1982hglaqe8pdnpophff'})
        self.assertTrue(response.status_code == status.HTTP_200_OK)
        self.assertTrue(len(content) == 1)
        self.assertTrue(content[0]['service_request_id'] == '1982hglaqe8pdnpophff')

    def test_get_by_service_request_ids(self):
        response, content = self.client.get('api/v1:feedback-list',
                                            {'service_request_id': '1982hglaqe8pdnpophff,2981hglaqe8pdnpoiuyt'})
        self.assertTrue(response.status_code == status.HTTP_200_OK)
        self.assertTrue(len(content) == 2)
        self.assertTrue(content[0]['service_request_id'] == '1982hglaqe8pdnpophff')
        self.assertTrue(content[1]['service_request_id'] == '2981hglaqe8pdnpoiuyt')

    def test_get_by_unexisting_request_id(self):
        response, content = self.client.get('api/v1:feedback-list', {'service_request_id': 'unexisting_req_id'})
        self.assertTrue(response.status_code == status.HTTP_200_OK)
        self.assertTrue(content == [])

    def test_get_by_service_code(self):
        service_code = '171'
        response, content = self.client.get('api/v1:feedback-list', {'service_code': service_code})
        self.assertTrue(response.status_code == status.HTTP_200_OK)
        for feedback in content:
            self.assertTrue(feedback['service_code'] == service_code)

    def test_get_by_start_date(self):
        start_date = '2015-06-23T15:51:11Z'
        expected_number_of_requests = 3
        response, content = self.client.get('api/v1:feedback-list', {'start_date': start_date})
        self.assertTrue(response.status_code == status.HTTP_200_OK)
        self.assertTrue(len(content) == expected_number_of_requests)
        for feedback in content:
            self.assertTrue(feedback['requested_datetime'] > start_date)

    def test_get_by_end_data(self):
        end_date = '2015-06-23T15:51:11Z'
        expected_number_of_requests = 1
        response, content = self.client.get('api/v1:feedback-list', {'end_date': end_date})
        self.assertTrue(response.status_code == status.HTTP_200_OK)
        self.assertTrue(len(content) == expected_number_of_requests)
        for request in content:
            self.assertTrue(request['requested_datetime'] < end_date)

    def test_get_by_status(self):
        feedback_status = 'open'
        expected_number_of_requests = 2
        response, content = self.client.get('api/v1:feedback-list', {'status': feedback_status})
        self.assertTrue(response.status_code == status.HTTP_200_OK)
        self.assertTrue(len(content) == expected_number_of_requests)
        for feedback in content:
            self.assertTrue(feedback['status'] == feedback_status)

    def test_by_description(self):
        search = 'some'
        response, content = self.client.get('api/v1:feedback-list', {'search': search})
        self.assertTrue(response.status_code == 200)
        self.assertTrue(search.lower() in content[0]['description'].lower())

    def test_get_with_extensions(self):
        response, content = self.client.get('api/v1:feedback-list',
                                            {'service_request_id': '1982hglaqe8pdnpophff', 'extensions': 'true'})
        self.assertTrue(response.status_code == status.HTTP_200_OK)
        self.assertTrue('extended_attributes' in content[0])

    def test_get_without_extensions(self):
        response, content = self.client.get('api/v1:feedback-list', {'service_request_id': '1982hglaqe8pdnpophff'})
        self.assertTrue(response.status_code == status.HTTP_200_OK)
        self.assertTrue('extended_attributes' not in content[0])

    def test_get_by_updated_after(self):
        updated_after = '2015-07-24T12:01:44Z'
        expected_number_of_requests = 3
        response, content = self.client.get('api/v1:feedback-list', {'updated_after': updated_after})
        self.assertTrue(response.status_code == status.HTTP_200_OK)
        self.assertTrue(len(content) == expected_number_of_requests)
        for feedback in content:
            self.assertTrue(feedback['updated_datetime'] > updated_after)

    def test_get_by_updated_before(self):
        updated_before = '2015-07-24T12:01:44Z'
        expected_number_of_requests = 1
        response, content = self.client.get('api/v1:feedback-list', {'updated_before': updated_before})
        self.assertTrue(response.status_code == status.HTTP_200_OK)
        self.assertTrue(len(content) == expected_number_of_requests)
        for feedback in content:
            self.assertTrue(feedback['updated_datetime'] < updated_before)

    def test_get_by_service_object(self):
        service_object_id = '10844'
        service_object_type = 'http://www.hel.fi/servicemap/v2'
        response, content = self.client.get('api/v1:feedback-list',
                                            {'extensions': 'true', 'service_object_id': 'service_object_id',
                                             'service_object_type': 'service_object_type'})
        self.assertTrue(response.status_code == status.HTTP_200_OK)
        for feedback in content:
            self.assertTrue(feedback['extended_attributes']['service_object_id'] == service_object_id)
            self.assertTrue(feedback['extended_attributes']['service_object_type'] == service_object_type)

    def test_get_by_service_object_id_without_type(self):
        service_object_id = '10844'
        response, content = self.client.get('api/v1:feedback-list', {'service_object_id': service_object_id})
        self.assertTrue(response.status_code == status.HTTP_400_BAD_REQUEST)

    def test_get_within_radius(self):
        lat = 60.187394
        long = 24.940773
        radius = 1000
        expected_number_of_requests = 3
        response, content = self.client.get('api/v1:feedback-list', {'lat': lat, 'long': long, 'radius': radius})
        self.assertTrue(response.status_code == status.HTTP_200_OK)
        self.assertTrue(len(content) == expected_number_of_requests)

        for feedback in content:
            self.assertTrue(feedback['distance'] < 1000)
