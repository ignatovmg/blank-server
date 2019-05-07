from django import forms
from django.contrib.auth.password_validation import password_validators_help_text_html
from django.core.validators import ValidationError
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.models import User

import re


class JobSubmitForm(forms.Form):
    jobname = forms.CharField(label='Job name',
                              help_text='Enter your job name here',
                              max_length=100,
                              required=False,
                              widget=forms.TextInput(attrs={'class': 'form-control',
                                                            'placeholder': 'Job name'}))


class SettingsForm(forms.Form):
    current_password = forms.CharField(label='Current password',
                                       max_length=100,
                                       required=True,
                                       help_text='Please enter your current password',
                                       widget=forms.PasswordInput(attrs={'class': 'form-control _password'}))

    password = forms.CharField(label='Password',
                               max_length=100,
                               required=True,
                               validators=[validate_password],
                               help_text=password_validators_help_text_html(),
                               widget=forms.PasswordInput(attrs={'class': 'form-control _password'}))


class AcademicEmailField(forms.EmailField):
    def validate(self, value):
        super().validate(value)
        if not re.match('.*@.*\.edu', value):
            raise ValidationError('Your e-mail must belong to ".edu" domain group')
        if User.objects.filter(email__exact=value).exists():
            raise ValidationError('Provided email is already in the database')


class SignUpForm(forms.Form):
    username = forms.CharField(label='Username *',
                               max_length=100,
                               required=True,
                               widget=forms.TextInput(attrs={'class': 'form-control',
                                                             'style': 'width: 40ch'}))

    email = AcademicEmailField(label='E-mail *',
                               required=True,
                               help_text='Please, provide a valid academic e-mail address (*.edu), we will use it to send you your password',
                               widget=forms.EmailInput(attrs={'class': 'form-control',
                                                              'style': 'width: 40ch'}))

    first_name = forms.CharField(label='First Name',
                                 max_length=100,
                                 required=False,
                                 widget=forms.TextInput(attrs={'class': 'form-control',
                                                               'style': 'width: 40ch'}))

    last_name = forms.CharField(label='Last Name',
                                max_length=100,
                                required=False,
                                widget=forms.TextInput(attrs={'class': 'form-control',
                                                              'style': 'width: 40ch'}))


def username_exists_validator(value):
    if not User.objects.filter(username__exact=value).exists():
        raise ValidationError('Sorry, we couldn\'t find the provided username')


class PasswordResetForm(forms.Form):
    username = forms.CharField(label='Username',
                               max_length=100,
                               required=True,
                               help_text='Please, provide your username',
                               validators=[username_exists_validator],
                               widget=forms.TextInput(attrs={'class': 'form-control'}))


def email_exists_validator(value):
    if not User.objects.filter(email__exact=value).exists():
        raise ValidationError('Sorry, provided email doesn\'t exist in the database')


class RetrieveUsernameForm(forms.Form):
    email = forms.EmailField(label='E-mail',
                             required=True,
                             help_text='Please, provide the academic e-mail address (*.edu), associated with your username',
                             validators=[email_exists_validator],
                             widget=forms.EmailInput(attrs={'class': 'form-control _email'}))

