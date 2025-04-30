from django import forms
from django.contrib.auth.models import User

TRAVEL_STYLE_CHOICES = [
    ('adventure', 'Adventure'),
    ('relax', 'Relaxed'),
    ('culture', 'Culture'),
    ('luxury', 'Luxury'),
]

class ProfileForm(forms.ModelForm):
    travel_style = forms.ChoiceField(choices=TRAVEL_STYLE_CHOICES)
    password = forms.CharField(widget=forms.PasswordInput(), required=False)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].disabled = True  # cannot edit username