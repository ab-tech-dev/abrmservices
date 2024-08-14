from django import forms

class ContactForm(forms.Form):
    first_name = forms.CharField(max_length=100)
    last_name = forms.CharField(max_length=100)
    email = forms.EmailField()
    phone = forms.IntegerField()
    text_area = forms.CharField(widget=forms.Textarea)


class ContactForm(forms.Form):
    first_name = forms.CharField(max_length=100)
    last_name = forms.CharField(max_length=100)
    email = forms.EmailField()
    phone = forms.IntegerField()
    text_area = forms.CharField(widget=forms.Textarea)