from django import forms
from django.contrib.auth.password_validation import password_validators_help_text_html
from django.core.validators import ValidationError
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.models import User

import re


def validate(input):
    if input <= 0:
        raise ValidationError('Summants must be > 0')


class JobSubmitForm(forms.Form):
    job_name = forms.CharField(label='Job name',
                               help_text='Enter your job name here',
                               max_length=100,
                               required=False)

    summant1 = forms.IntegerField(label='Summant 1 *',
                                  help_text='Provide summant 1',
                                  required=True,
                                  validators=[validate])

    summant2 = forms.IntegerField(label='Summant 2 *',
                                  help_text='Provide summant 2',
                                  required=True,
                                  validators=[validate])

    def clean(self):
        cleaned_data = super().clean()
        s1, s2 = cleaned_data.get('summant1'), cleaned_data.get('summant2')
        if (s1 is not None) and (s2 is not None) and s2 % s1 != 0:
            self.add_error('summant2', 'Summant 2 must be a multiple of Summant 1')

        return cleaned_data


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
        if not re.match(r'.*@.*\.edu', value):
            raise ValidationError('Your e-mail must belong to ".edu" domain group')
        if User.objects.filter(email__exact=value).exists():
            raise ValidationError('Provided email is already in the database')


class SignUpForm(forms.Form):
    email = AcademicEmailField(label='E-mail *',
                               required=True,
                               max_length=1000,
                               help_text='Please, provide a valid academic e-mail address (*.edu), we will use it to send you your password',
                               widget=forms.EmailInput(attrs={'class': 'form-control',
                                                              'style': 'width: 40ch'}))

    first_name = forms.CharField(label='First Name',
                                 max_length=1000,
                                 required=False,
                                 widget=forms.TextInput(attrs={'class': 'form-control',
                                                               'style': 'width: 40ch'}))

    last_name = forms.CharField(label='Last Name',
                                max_length=1000,
                                required=False,
                                widget=forms.TextInput(attrs={'class': 'form-control',
                                                              'style': 'width: 40ch'}))


def username_not_exists_validator(value):
    if not User.objects.filter(username__exact=value).exists():
        raise ValidationError('Sorry, we couldn\'t find the e-mail you provided')


class PasswordResetForm(forms.Form):
    username = forms.CharField(label='E-mail',
                               required=True,
                               max_length=1000,
                               help_text='Please, enter your e-mail address',
                               validators=[username_not_exists_validator],
                               widget=forms.TextInput(attrs={'class': 'form-control',
                                                             'style': 'width: 40ch'}))
