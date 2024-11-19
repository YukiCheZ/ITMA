from django import forms
from .models import APIKey

class APIKeyForm(forms.ModelForm):
    class Meta:
        model = APIKey
        fields = ['api_key']
