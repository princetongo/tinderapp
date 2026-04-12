from django import forms
from .models import Profile, ProfilePhoto


class ProfileForm(forms.ModelForm):
    birth_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=False
    )

    class Meta:
        model = Profile
        fields = [
            'first_name', 'last_name', 'bio', 'birth_date',
            'gender', 'interested_in', 'location',
            'job_title', 'company', 'education'
        ]
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Tell people about yourself...'}),
            'location': forms.TextInput(attrs={'placeholder': 'City, Country'}),
            'job_title': forms.TextInput(attrs={'placeholder': 'What do you do?'}),
            'company': forms.TextInput(attrs={'placeholder': 'Where do you work?'}),
            'education': forms.TextInput(attrs={'placeholder': 'Where did you study?'}),
        }


class PhotoUploadForm(forms.ModelForm):
    class Meta:
        model = ProfilePhoto
        fields = ['image', 'is_primary']
        widgets = {
            'image': forms.FileInput(attrs={'accept': 'image/*'})
        }
