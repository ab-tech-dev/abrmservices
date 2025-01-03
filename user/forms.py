from django import forms
from django.contrib.auth import get_user_model

User = get_user_model()

class RegisterForm(forms.ModelForm):
    password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Enter Password',
            'class': 'form-control',
            'style': 'padding: 10px; border: 1px solid #ddd; border-radius: 4px; font-size: 16px;',
        })
    )
    re_password = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Confirm Password',
            'class': 'form-control',
            'style': 'padding: 10px; border: 1px solid #ddd; border-radius: 4px; font-size: 16px;',
        })
    )
    is_realtor = forms.BooleanField(
        label='Are you a realtor?',
        required=False,  # Checkbox is optional
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input',
            'style': 'margin-left: 10px; width: 20px; height: 20px;',
        })
    )

    class Meta:
        model = User
        fields = ['name', 'email']

        widgets = {
            'email': forms.EmailInput(attrs={
                'placeholder': 'Enter Email',
                'class': 'form-control',
                'style': 'padding: 10px; border: 1px solid #ddd; border-radius: 4px; font-size: 16px;',
            }),
            'name': forms.TextInput(attrs={
                'placeholder': 'Enter Name',
                'class': 'form-control',
                'style': 'padding: 10px; border: 1px solid #ddd; border-radius: 4px; font-size: 16px;',
            })
        }

    def clean_re_password(self):
        password = self.cleaned_data.get('password')
        re_password = self.cleaned_data.get('re_password')

        if password != re_password:
            raise forms.ValidationError("Passwords do not match")
        return re_password


class LoginForm(forms.Form):
    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={
            'placeholder': 'Enter Email',
            'class': 'form-control',
            'style': 'padding: 10px; border: 1px solid #ddd; border-radius: 4px; font-size: 16px;',
        })
    )
    password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Enter Password',
            'class': 'form-control',
            'style': 'padding: 10px; border: 1px solid #ddd; border-radius: 4px; font-size: 16px;',
        })
    )
