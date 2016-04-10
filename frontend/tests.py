from django.core.urlresolvers import reverse
from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils.encoding import force_text
import json

from .forms import *


# Test some developer functions
class BasicTest(TestCase):
    fixtures = ["test_data.json"]

    # Test that getting all top level pages returns proper code and uses right template
    def test_get_pages(self):
        response = self.client.get(reverse("mainpage"))
        self.assertTemplateUsed(response, "mainpage.html")
        self.assertContains(response, "Testipalaute", 1, 200)

        response = self.client.get(reverse("feedback_list"))
        self.assertTemplateUsed(response, "feedback_list.html")
        self.assertContains(response, "Toinen", 2, 200)

        response = self.client.get(reverse("feedback_details", args=[2]))
        self.assertTemplateUsed(response, "feedback_details.html")
        self.assertContains(response, "testipalaute", 2, 200)

        response = self.client.get(reverse("feedback_form"))
        self.assertTemplateUsed(response, "feedback_form/closest.html")
        self.assertContains(response, "Sijainti", 1, 200)

        response = self.client.get(reverse("map"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "map.html")
        self.assertInHTML('<div id="map" class="map-main"></div>', response.content.decode('UTF-8', 'ignore'))

        response = self.client.get(reverse("statistics"))
        self.assertTemplateUsed(response, "statistics.html")
        self.assertContains(response, "aihealueiden", 1, 200)

        response = self.client.get(reverse("department"))
        self.assertTemplateUsed(response, "department.html")
        self.assertContains(response, "virastojen", 1, 200)

        response = self.client.get(reverse("charts"))
        self.assertTemplateUsed(response, "charts.html")
        self.assertContains(response, "Korjausajat", 1, 200)

        response = self.client.get(reverse("about"))
        self.assertTemplateUsed(response, "about.html")
        self.assertContains(response, "Tietoja sivustosta", 1, 200)

    # Test Feedback list having correct first feedback title
    def test_feedback_list(self):
        response = self.client.get(reverse("feedback_list"))
        self.assertTemplateUsed(response, "feedback_list.html")
        self.assertEqual(response.context["feedbacks"][0].title, "Testipalaute")
        self.assertEqual(response.context["feedbacks"][1].title, "Toinen testipalaute")
        self.assertEqual(len(response.context["feedbacks"]), 2)
        self.assertContains(response, "Lorem ipsum", None, 200)
        self.assertContains(response, "08.04.2016", 1)

    # Test Feedback list returning empty set
    def test_feedback_list_empty(self):
        response = self.client.get(reverse("feedback_list"), {"service_code": "0000"})
        self.assertTemplateUsed(response, "feedback_list.html")
        self.assertContains(response, "Ei palautteita!", 1, 200)
        self.assertEqual(len(response.context["feedbacks"]), 0)

    # Test having valid info in FeedbackFormBasicInfo
    def test_basic_info_form_valid(self):
        form_data = {
            "title": "Simple title",
            "description": "Some description"
        }

        form = FeedbackFormBasicInfo(form_data)
        self.assertTrue(form.is_valid())

    # Test having invalid info in FeedbackFormBasicInfo.
    # Also check that error messages match
    def test_basic_info_form_invalid(self):
        form_data = {
            "title": "",
            "description": ""
        }

        form = FeedbackFormBasicInfo(form_data)
        self.assertEqual(form.errors, {
            "title": ["This field is required."],
            "description": ["This field is required."]
        })

    # Test getting filelist from media_upload 
    def test_media_upload(self):
        response = self.client.post(reverse("media_upload"), {"action": "get_files", "form_id": " "})
        self.assertJSONEqual(str(response.content, encoding='utf8'), {"status": "success", "files": []})

        response = self.client.post(reverse("media_upload"), {"action": "delete_file", "form_id": " ", "server_filename": "123.jpg"})
        self.assertJSONEqual(str(response.content, encoding='utf8'), {"status": "success"})

        file = SimpleUploadedFile("file.jpg", b"file_content", content_type="image/jpeg")
        response = self.client.post(reverse("media_upload"), {"action": "upload_file", "form_id": " ", "file": file})
        j = json.loads(str(response.content, encoding='utf8'))
        self.assertEqual(j["status"], "success")
        self.assertEqual(len(j["filename"]), 36)

    # Testing feedback voting using invalid ID
    def test_vote_feedback_invalid(self):
        response = self.client.post(reverse("vote_feedback"), {"id": "-1"})

        self.assertJSONEqual(str(response.content, encoding='utf8'),
                             {"status": "error",
                              "message": "Ääntä ei voitu tallentaa. Palautetta ei löydetty!"})

    # Testing feedback voting using valid ID
    def test_vote_feedback_valid(self):
        response = self.client.post(reverse("vote_feedback"), {"id": "1"})

        self.assertJSONEqual(str(response.content, encoding='utf8'),
                             {"status": "success",
                              "message": "Kiitos, äänesi on rekisteröity!"})
