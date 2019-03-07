from django import forms


class JobSubmitForm(forms.Form):
    jobname = forms.CharField(label='Job name',
                              help_text='Enter your job name here',
                              max_length=100,
                              widget=forms.TextInput(attrs={'class': 'form-control',
                                                            'placeholder': 'Job name'}))


class SignUpForm(forms.Form):
    username = forms.CharField(label='Username *',
                               max_length=100,
                               required=True,
                               widget=forms.TextInput(attrs={'class': 'form-control'}))

    password = forms.CharField(label='Password *',
                               max_length=100,
                               required=True,
                               widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    email = forms.EmailField(label='E-mail *',
                             required=True,
                             widget=forms.EmailInput(attrs={'class': 'form-control'}))

    first_name = forms.CharField(label='First Name',
                                 max_length=100,
                                 required=False,
                                 widget=forms.TextInput(attrs={'class': 'form-control'}))

    last_name = forms.CharField(label='Last Name',
                                max_length=100,
                                required=False,
                                widget=forms.TextInput(attrs={'class': 'form-control'}))
