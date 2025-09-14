from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
from .models import Room

# ฟอร์มสมัครสมาชิก (User Registration)
class CustomUserCreationForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super(CustomUserCreationForm, self).__init__(*args, **kwargs)
        
        self.fields['username'].widget.attrs.update({'placeholder': 'Username...'})
        self.fields['email'].widget.attrs.update({'placeholder': 'Email...'})
        
        self.fields['password1'].widget.attrs.update({'placeholder': 'Password...'})
        self.fields['password2'].widget.attrs.update({'placeholder': 'Confirm Password...'})

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email')

# ฟอร์มห้องเรียน (Room)
class RoomForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = [
            'room_code', 
            'name', 
            'capacity', 
            'start_time_available', 
            'end_time_available', 
            'status', 
            'image'
        ]
        widgets = {
            'start_time_available': forms.TimeInput(attrs={'type': 'time'}),
            'end_time_available': forms.TimeInput(attrs={'type': 'time'}),
        }