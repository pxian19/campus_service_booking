from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import RegisterForm, LoginForm


# Register a new user account (student/staff), then log them in
def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        
        # If validation passes, save user to database and log them in
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful!')
            return redirect('home')
        else:
            # If form is invalid, show errors on the same page
            messages.error(request, 'Please correct the errors below.')
    else:
        form = RegisterForm()
    return render(request, 'booking/register.html', {'form': form})


# Log in with email + password
def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        
        # Validate basic form fields first (email format, etc.)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = authenticate(request, username=email, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, 'Welcome back!')
                return redirect('home')
            else:
                # Authentication failed: show an error message
                messages.error(request, 'Invalid email or password.')
    else:
        # GET request: show an empty login form
        form = LoginForm()
        
    return render(request, 'booking/login.html', {'form': form})


# Log out the current user and return them to the login page
def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('login')


# Role-based home page: staff sees staff home; student sees student home
@login_required
def home_view(request):
    if request.user.role == 'staff':
        return render(request, 'booking/staff_home.html')
    
    return render(request, 'booking/student_home.html')