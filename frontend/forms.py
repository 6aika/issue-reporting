from django import forms

class FeedbackForm1(forms.Form):
	address = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Enter address..."}))
	latitude = forms.FloatField(widget=forms.HiddenInput({'class': 'form-control', 'placeholder': "Latitude"}))
	longitude = forms.FloatField(widget=forms.HiddenInput({'class': 'form-control', 'placeholder': "Longitude"}))

class FeedbackForm2(forms.Form):
	category = forms.IntegerField(required=True, widget=forms.HiddenInput(attrs={'class': 'form-control', 'placeholder': "Enter category..."}))

class FeedbackForm3(forms.Form):
	title = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Anna otsikko..."}))
	description = forms.CharField(required=True, widget=forms.Textarea(attrs={'rows': 8, 'maxlength': 5000, 'class': 'form-control', 'placeholder': "Kirjoita tarkka kuvaus..."}))

