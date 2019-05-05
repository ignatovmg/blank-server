from django import forms
from django.contrib.auth.password_validation import password_validators_help_text_html
from django.core.validators import validate_slug, ValidationError
import re


class JobSubmitForm(forms.Form):
    jobname = forms.CharField(label='Job name',
                              help_text='Enter your job name here',
                              max_length=100,
                              required=False,
                              widget=forms.TextInput(attrs={'class': 'form-control',
                                                            'placeholder': 'Job name'}))


class AcademicEmailField(forms.EmailField):
    def validate(self, value):
        super().validate(value)
        if not re.match('.*@.*\.edu', value):
            raise ValidationError('Your e-mail must belong to ".edu" domain group')


class SignUpForm(forms.Form):
    username = forms.CharField(label='Username *',
                               max_length=100,
                               required=True,
                               widget=forms.TextInput(attrs={'class': 'form-control'}))

    password = forms.CharField(label='Password *',
                               max_length=100,
                               required=True,
                               help_text=password_validators_help_text_html(),
                               widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    email = AcademicEmailField(label='E-mail *',
                               required=True,
                               help_text='Please provide academic e-mail address (*.edu)',
                               widget=forms.EmailInput(attrs={'class': 'form-control'}))

    first_name = forms.CharField(label='First Name',
                                 max_length=100,
                                 required=False,
                                 widget=forms.TextInput(attrs={'class': 'form-control'}))

    last_name = forms.CharField(label='Last Name',
                                max_length=100,
                                required=False,
                                widget=forms.TextInput(attrs={'class': 'form-control'}))
