from django.test import TestCase
from django.core.exceptions import *
from django.core.urlresolvers import reverse
from api.models import *
from .forms import *

# Test some developer functions
class BasicTest(TestCase):

    # Test getting mainpage
    def test_get_mainpage(self):
        response = self.client.get(reverse("mainpage"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "mainpage.html")

    # Test having valid info in FeedbackFormBasicInfo
    def test_basic_info_form_valid(self):
        form_data = {
            "title":        "Simple title",
            "description":  "Some description"
        }

        form = FeedbackFormBasicInfo(form_data)
        self.assertTrue(form.is_valid())

    # Test having invalid info in FeedbackFormBasicInfo.
    # Also check that error messages match
    def test_basic_info_form_invalid(self):
        form_data = {
            "title":        "",
            "description":  ""
        }

        form = FeedbackFormBasicInfo(form_data)
        self.assertEqual(form.errors, {
            "title":        ["This field is required."],
            "description":  ["This field is required."]
        })

    # Test getting filelist from media_upload 
    def test_media_upload(self):
        response = self.client.post(reverse("media_upload"), {"action": "get_files", "form_id": " "})
        self.assertJSONEqual(str(response.content, encoding='utf8'), {"status": "success", "files": []})

    # Testing feedback voting using invalid ID
    def test_vote_feedback(self):
        response = self.client.post(reverse("vote_feedback"), {"id": "-1"})

        self.assertJSONEqual(str(response.content, encoding='utf8'), 
            {   "status": "error", 
                "message": "Ääntä ei voitu tallentaa. Palautetta ei löydetty!"})

