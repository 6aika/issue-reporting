from django import forms


class FeedbackFormClosest(forms.Form):
    latitude = forms.FloatField(widget=forms.HiddenInput(attrs={'class': 'form-control', 'placeholder': "Latitude"}))
    longitude = forms.FloatField(widget=forms.HiddenInput(attrs={'class': 'form-control', 'placeholder': "Longitude"}))
    service_object_id = forms.CharField(max_length=10, widget=forms.HiddenInput(), required=False)
    form_id = forms.CharField(required=False, max_length=50, widget=forms.HiddenInput())


class FeedbackFormCategory(forms.Form):
    service_code = forms.CharField(widget=forms.HiddenInput(
            attrs={'class': 'form-control', 'placeholder': "Enter category..."}))


class FeedbackFormBasicInfo(forms.Form):
    title = forms.CharField(max_length=100,
                            widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Anna otsikko..."}))
    description = forms.CharField(widget=forms.Textarea(
            attrs={'rows': 8, 'maxlength': 5000, 'class': 'form-control', 'placeholder': "Kirjoita tarkka kuvaus..."}))


class FeedbackFormContact(forms.Form):
    first_name = forms.CharField(max_length=100, required=False,
                                 widget=forms.TextInput(
                                     attrs={'class': 'form-control', 'placeholder': "Anna etunimesi..."}))
    last_name = forms.CharField(max_length=100, required=False,
                                widget=forms.TextInput(
                                    attrs={'class': 'form-control', 'placeholder': "Anna sukunimesi..."}))
    email = forms.EmailField(max_length=100, required=False, widget=forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': "Anna sähköpostiosoitteesi..."}))
    phone = forms.CharField(max_length=100, required=False, widget=forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': "Anna puhelinnumerosi..."}))
