from django import forms
from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser, CustomerProfile

class CustomUserCreationForm(UserCreationForm):
    
    class Meta(UserCreationForm.Meta):
        model = CustomUser


class CustomUserChangeForm(UserChangeForm):

    class Meta(UserChangeForm.Meta):
        model = CustomUser


"""class CustomerProfileChangeForm(ModelForm) :

    class Meta :
        model = CustomerProfile
        exclude = ()"""


class UserSignUpForm(forms.Form):
    username = forms.CharField(
        required = True,
        label = 'Username',
        max_length = 32
    )
    email = forms.CharField(
        required = True,
        label = 'Email',
        max_length = 32,
    )
    password = forms.CharField(
        required = True,
        label = 'Password',
        max_length = 32,
        widget = forms.PasswordInput()
    )