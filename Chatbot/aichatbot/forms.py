from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import CustomUser

class RegisterForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    mobile_number = forms.CharField(max_length=15, required=True)
    
    class Meta:
        model = CustomUser
        fields = ["first_name", "last_name", "mobile_number", "email", "username", "password1", "password2"]

class LoginForm(AuthenticationForm):
    username = forms.CharField(label="Email or Username")
