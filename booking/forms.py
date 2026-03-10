from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Booking, TimeSlot


class RegisterForm(UserCreationForm):
    """
    Registration form for campus booking system.
    
    Key rules:
    - Only University of Glasgow emails are allowed (student.gla.ac.uk / gla.ac.uk)
    - Users must choose a role (student or staff) for role-based access control
    """
    ROLE_CHOICES = [
        ('student', 'Student'),
        ('staff', 'Staff'),
    ]

    role = forms.ChoiceField(choices=ROLE_CHOICES)

    class Meta:
        model = User
        fields = ['email', 'username', 'first_name', 'last_name', 'role', 'password1', 'password2']

    # Validate that email belongs to University of Glasgow
    def clean_email(self):
        email = self.cleaned_data.get('email')
        allowed_domains = ['student.gla.ac.uk', 'gla.ac.uk']
        domain = email.split('@')[-1]
        if domain not in allowed_domains:
            raise forms.ValidationError('Please use a University of Glasgow email address.')
        return email


# Login form using email and password


from django.utils import timezone
class LoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)


class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['notes']


class TimeSlotForm(forms.ModelForm):
    class Meta:
        model = TimeSlot
        fields = ['service', 'date', 'start_time', 'end_time']

    def clean(self):
        cleaned_data = super().clean()
        date = cleaned_data.get('date')
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')

        if start_time and end_time and start_time >= end_time:
            raise forms.ValidationError("End time must be after start time.")

        if date and date < timezone.now().date():
            raise forms.ValidationError("You cannot create a time slot in the past.")

        return cleaned_data