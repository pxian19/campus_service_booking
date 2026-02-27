from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User


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
class LoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)