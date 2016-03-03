from django import forms
from multiupload.fields import MultiFileField

class FeedbackFormClosest(forms.Form):
    latitude = forms.FloatField(widget=forms.HiddenInput(
        attrs={'class': 'form-control', 'placeholder': "Latitude"}))
    longitude = forms.FloatField(widget=forms.HiddenInput(
        attrs={'class': 'form-control', 'placeholder': "Longitude"}))


class FeedbackFormCategory(forms.Form):
    service_code = forms.CharField(widget=forms.HiddenInput(
        attrs={'class': 'form-control', 'placeholder': "Enter category..."}))


class FeedbackForm3(forms.Form):
	title = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Anna otsikko..."}))
	description = forms.CharField(widget=forms.Textarea(attrs={'rows': 8, 'maxlength': 5000, 'class': 'form-control', 'placeholder': "Kirjoita tarkka kuvaus..."}))
	#image = forms.FileField(required=False, allow_empty_file=True)
	attachments = MultiFileField(min_num=1, max_num=3, max_file_size=1024*1024*5)

class FeedbackFormContact(forms.Form):
	first_name = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Etunimesi..."}))
	last_name = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Sukunimesi..."}))
	email = forms.EmailField(max_length=100, required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Sähköpostiosoitteesi..."}))
	phone = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Puhelinnumerosi..."}))
