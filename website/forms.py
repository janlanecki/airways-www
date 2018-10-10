"""forms in website"""
from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from website.models import Ticket


class SearchForm(forms.Form):
    """form used for searching flights"""
    airport_from = forms.CharField(max_length=150, required=False,
                                   widget=forms.TextInput(attrs={'placeholder': 'From'}))
    airport_to = forms.CharField(max_length=150, required=False,
                                 widget=forms.TextInput(attrs={'placeholder': 'To'}))
    day_from = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=False)
    day_to = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=False)


class TicketForm(forms.ModelForm):
    """form used to add new tickets"""
    class Meta: # pylint: disable=missing-docstring,too-few-public-methods
        model = Ticket
        fields = ['first_name', 'last_name', 'seats']


class SignupForm(forms.Form):
    """form used to sign up user"""
    username = forms.CharField(max_length=150, label='Username')
    password = forms.CharField(max_length=255, label='Password', widget=forms.PasswordInput)

    def clean(self):
        if User.objects.filter(username=self.cleaned_data['username']).exists():
            raise ValidationError('User with this username already exists.')
