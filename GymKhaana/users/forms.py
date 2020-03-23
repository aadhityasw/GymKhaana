from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        #fields = ('username', 'email', 'is_student', 'is_manager', 'is_trainer')

class CustomUserChangeForm(UserChangeForm):

    class Meta(UserChangeForm.Meta):
        model = CustomUser
        #fields = ('username', 'email', 'is_student', 'is_manager', 'is_trainer')