from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import List, UserProfile

class ListPromptForm(forms.Form):
    prompt = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        label="What kind of list would you like to generate?",
        help_text="Example: 'Top 10 sci-fi movies of all time' or 'Best practices for Python development'"
    )

class ListForkForm(forms.ModelForm):
    class Meta:
        model = List
        fields = ['is_public']
        labels = {
            'is_public': 'Make this list public?'
        }

class ListEditForm(forms.ModelForm):
    class Meta:
        model = List
        fields = ['title', 'content', 'is_public']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 10})
        }

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['bio']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 3})
        } 