from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import RegisterForm, LoginForm, BookingForm, TimeSlotForm
from .models import Service, TimeSlot, Booking

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


@login_required
def service_list_view(request):
    services = Service.objects.filter(is_active=True)
    return render(request, 'booking/service_list.html', {
        'services': services
    })
@login_required
def slot_list_view(request, service_id):
    service = Service.objects.get(id=service_id)
    slots = TimeSlot.objects.filter(service=service, is_available=True)

    return render(
        request,
        'booking/slot_list.html',
        {
            'service': service,
            'slots': slots
        }
    )
@login_required
def create_booking_view(request, slot_id):
    slot = TimeSlot.objects.get(id=slot_id)

    if not slot.is_available:
        messages.error(request, 'This slot is no longer available.')
        return redirect('slot_list', service_id=slot.service.id)

    existing_booking = Booking.objects.filter(
        user=request.user,
        time_slot=slot,
        status='confirmed'
    ).exists()

    if existing_booking:
        messages.error(request, 'You have already booked this slot.')
        return redirect('slot_list', service_id=slot.service.id)

    booking = Booking.objects.create(
        user=request.user,
        time_slot=slot,
        status='confirmed'
    )

    slot.is_available = False
    slot.save()

    return render(request, 'booking/booking_confirm.html', {
        'booking': booking
    })
@login_required
def my_bookings_view(request):
    bookings = Booking.objects.filter(user=request.user).order_by('-id')
    return render(request, 'booking/my_bookings.html', {
        'bookings': bookings
    })
@login_required
def cancel_booking_view(request, booking_id):

    if request.method != 'POST':
        return redirect('my_bookings')

    booking = get_object_or_404(Booking, id=booking_id, user=request.user)

    if booking.status == 'confirmed':
        booking.status = 'cancelled'
        booking.save()

        slot = booking.time_slot
        slot.is_available = True
        slot.save()

        messages.success(request, 'Booking cancelled successfully.')

    return redirect('my_bookings')
@login_required
def staff_manage_slots_view(request):
    if request.user.role != 'staff':
        messages.error(request, 'Access denied.')
        return redirect('home')

    slots = TimeSlot.objects.all().order_by('date', 'start_time')

    if request.method == 'POST':
        form = TimeSlotForm(request.POST)
        if form.is_valid():
            slot = form.save(commit=False)
            slot.created_by_staff = request.user
            slot.save()
            messages.success(request, 'Time slot created successfully.')
            return redirect('staff_manage_slots')
    else:
        form = TimeSlotForm()

    return render(request, 'manage_slots.html', {
        'form': form,
        'slots': slots,
    })


@login_required
def staff_booking_list_view(request):
    if request.user.role != 'staff':
        messages.error(request, 'Access denied.')
        return redirect('home')

    bookings = Booking.objects.all().order_by('-created_at')

    return render(request, 'booking/staff_booking_list.html', {
        'bookings': bookings,
    })