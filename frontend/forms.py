from django import forms

class FeedbackForm1(forms.Form):
	address = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Enter address..."}))

class FeedbackForm2(forms.Form):
	category = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Enter category..."}))

class FeedbackForm3(forms.Form):
	title = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Enter title..."}))
	description = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Enter description..."}))

