from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import date, timedelta, time, datetime
from .forms import RegisterForm, LoginForm, BookingForm, TimeSlotForm
from .models import Service, ServiceType, TimeSlot, Booking, User

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
        # Get services created by this staff member
        managed_services = Service.objects.filter(
            time_slots__created_by_staff = request.user
        ).distinct()

        # Count active bookings for this staff's services
        active_bookings_count = Booking.objects.filter(
            time_slot__service__in = managed_services,
            status='confirmed'
        ).count()

        return render(request, 'booking/staff_home.html', {
            'managed_services': managed_services,
            'active_bookings_count': active_bookings_count,
        })

    service_types = ServiceType.objects.all()
    return render(request, 'booking/student_home.html', {
        'service_types': service_types
    })

# student views
@login_required
def service_list_view(request):
    services = Service.objects.filter(is_active = True)
    return render(request, 'booking/service_list.html', {
        'services': services
    })
    
@login_required
def slot_list_view(request, service_id):
    service = get_object_or_404(Service, id = service_id)
    slots = TimeSlot.objects.filter(service = service, is_available = True)
    return render(request, 'booking/slot_list.html', {
        'service': service,
        'slots': slots
    })

@login_required
def slots_by_type_view(request, type_id):
    service_type = get_object_or_404(ServiceType, id = type_id)
    services = Service.objects.filter(service_type = service_type, is_active = True)

    today = date.today()
    end_date = today + timedelta(days = 2)  # today + next 2 days = 3 days total
    now = timezone.now().time()

    slots = TimeSlot.objects.filter(
        service__in = services,
        is_available = True,
        date__gte = today,
        date__lte = end_date,
    ).order_by('date', 'start_time')

    # Filter out time slots that have already passed today
    filtered_slots = []
    for slot in slots:
        if slot.date == today and slot.start_time <= now:
            continue
        filtered_slots.append(slot)

    return render(request, 'booking/slot_list.html', {
        'service_type': service_type,
        'slots': filtered_slots,
    })
    
@login_required
def create_booking_view(request, slot_id):
    slot = get_object_or_404(TimeSlot, id=slot_id)

    if not slot.is_available:
        messages.error(request, 'This slot is no longer available.')
        return redirect('slots_by_type', type_id=slot.service.service_type.id)

    existing_booking = Booking.objects.filter(
        user=request.user,
        time_slot=slot,
        status='confirmed'
    ).exists()

    if existing_booking:
        messages.error(request, 'You have already booked this slot.')
        return redirect('slots_by_type', type_id=slot.service.service_type.id)

    # Show the confirmation page with notes form
    return render(request, 'booking/booking_confirm.html', {
        'slot': slot,
    })
    
@login_required
# Creating the booking after the student submits the motes form
def confirm_booking_view(request, slot_id):
    if request.method != 'POST':
        return redirect('create_booking', slot_id=slot_id)

    slot = get_object_or_404(TimeSlot, id=slot_id)

    if not slot.is_available:
        messages.error(request, 'This slot is no longer available.')
        return redirect('slots_by_type', type_id=slot.service.service_type.id)

    existing_booking = Booking.objects.filter(
        user=request.user,
        time_slot=slot,
        status='confirmed'
    ).exists()

    if existing_booking:
        messages.error(request, 'You have already booked this slot.')
        return redirect('slots_by_type', type_id=slot.service.service_type.id)

    notes = request.POST.get('notes', '').strip()

    # For Repair, notes are required
    if slot.service.service_type.name == 'Repair' and not notes:
        messages.error(request, 'Please describe what needs to be repaired.')
        return render(request, 'booking/booking_confirm.html', {
            'slot': slot,
        })

    booking = Booking.objects.create(
        user=request.user,
        time_slot=slot,
        notes=notes,
        status='confirmed'
    )

    slot.is_available = False
    slot.save()

    return render(request, 'booking/booking_success.html', {
        'booking': booking
    })


@login_required
def my_bookings_view(request):
    bookings = Booking.objects.filter(user = request.user).order_by('-id')

    now = timezone.now()
    for booking in bookings:
        if booking.status == 'confirmed':
            slot_start = timezone.make_aware(
                datetime.combine(booking.time_slot.date, booking.time_slot.start_time)
            )
            hours_until = (slot_start - now).total_seconds() / 3600
            booking.can_cancel = hours_until > 24
        else:
            booking.can_cancel = False

    return render(request, 'booking/my_bookings.html', {
        'bookings': bookings
    })
    
@login_required
def cancel_booking_view(request, booking_id):
    if request.method != 'POST':
        return redirect('my_bookings')

    booking = get_object_or_404(Booking, id = booking_id, user = request.user)

    if booking.status == 'confirmed':
        # Check 24-hour cancellation policy
        now = timezone.now()
        slot_start = timezone.make_aware(
            datetime.combine(booking.time_slot.date, booking.time_slot.start_time)
        )
        hours_until = (slot_start - now).total_seconds() / 3600

        if hours_until <= 24:
            messages.error(request, 'Cannot cancel within 24 hours of the appointment.')
            return redirect('my_bookings')

        booking.status = 'cancelled'
        booking.cancelled_at = timezone.now()
        booking.save()

        slot = booking.time_slot
        slot.is_available = True
        slot.save()

        messages.success(request, 'Booking cancelled successfully.')

    return redirect('my_bookings')

# staff views
@login_required
# Staff creates a new Counselling/Tutor service with time slots
def staff_create_service_view(request):
    if request.user.role != 'staff':
        messages.error(request, 'Access denied.')
        return redirect('home')

    # Only allow creating Counselling and Tutor services
    allowed_types = ServiceType.objects.filter(name__in=['Counselling', 'Tutor'])
    today = date.today()
    max_date = today + timedelta(days=2)

    if request.method == 'POST':
        type_id = request.POST.get('service_type')
        staff_name = request.POST.get('staff_name', '').strip()
        room = request.POST.get('room', '').strip()
        slot_date = request.POST.get('slot_date')
        start_time_str = request.POST.get('start_time')
        end_time_str = request.POST.get('end_time')

        # Validate inputs
        if not all([type_id, staff_name, room, slot_date, start_time_str, end_time_str]):
            messages.error(request, 'All fields are required.')
            return render(request, 'booking/staff_create_service.html', {
                'allowed_types': allowed_types,
                'today': today.isoformat(),
                'max_date': max_date.isoformat(),
            })
        service_type = get_object_or_404(ServiceType, id=type_id)

        # Validate date is within 3 days
        try:
            slot_date_obj = datetime.strptime(slot_date, '%Y-%m-%d').date()
        except ValueError:
            messages.error(request, 'Invalid date format.')
            return render(request, 'booking/staff_create_service.html', {
                'allowed_types': allowed_types,
                'today': today.isoformat(),
                'max_date': max_date.isoformat(),
            })

        if slot_date_obj < today or slot_date_obj > max_date:
            messages.error(request, 'Date must be within the next 3 days (today included).')
            return render(request, 'booking/staff_create_service.html', {
                'allowed_types': allowed_types,
                'today': today.isoformat(),
                'max_date': max_date.isoformat(),
            })

        # Parse times
        try:
            start_t = datetime.strptime(start_time_str, '%H:%M').time()
            end_t = datetime.strptime(end_time_str, '%H:%M').time()
        except ValueError:
            messages.error(request, 'Invalid time format.')
            return render(request, 'booking/staff_create_service.html', {
                'allowed_types': allowed_types,
                'today': today.isoformat(),
                'max_date': max_date.isoformat(),
            })

        if start_t >= end_t:
            messages.error(request, 'End time must be after start time.')
            return render(request, 'booking/staff_create_service.html', {
                'allowed_types': allowed_types,
                'today': today.isoformat(),
                'max_date': max_date.isoformat(),
            })

        # Get or create the service
        if slot_date_obj == today:
            now_time = timezone.localtime().time()
            if start_t <= now_time:
                messages.error(request, 'Cannot create a slot in the past. Start time must be after the current time.')
                return render(request, 'booking/staff_create_service.html', {
                    'allowed_types': allowed_types,
                    'today': today.isoformat(),
                    'max_date': max_date.isoformat(),
                })
                
        service, created = Service.objects.get_or_create(
            name = staff_name,
            service_type = service_type,
            defaults = {'location': room, 'is_active': True}
        )
        if not created:
            service.location = room
            service.save()

        # Check for duplicate slot
        existing = TimeSlot.objects.filter(
            service = service,
            date = slot_date_obj,
            start_time = start_t,
            end_time = end_t,
        ).exists()

        if existing:
            messages.error(request, 'A slot with the same date and time already exists for this service.')
            return render(request, 'booking/staff_create_service.html', {
                'allowed_types': allowed_types,
                'today': today.isoformat(),
                'max_date': max_date.isoformat(),
            })

        # Create the time slot
        TimeSlot.objects.create(
            service = service,
            date = slot_date_obj,
            start_time = start_t,
            end_time = end_t,
            is_available = True,
            created_by_staff = request.user,
        )

        messages.success(request, f'Service slot created: {staff_name} on {slot_date_obj} {start_t.strftime("%H:%M")}-{end_t.strftime("%H:%M")}')
        return redirect('home')

    return render(request, 'booking/staff_create_service.html', {
        'allowed_types': allowed_types,
        'today': today.isoformat(),
        'max_date': max_date.isoformat(),
    })


@login_required
def staff_manage_slots_view(request):
    if request.user.role != 'staff':
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    # Only show slots for services this staff member created
    slots = TimeSlot.objects.filter(created_by_staff=request.user).order_by('date', 'start_time')

    if request.method == 'POST':
        form = TimeSlotForm(request.POST)
        if form.is_valid():
            slot = form.save(commit = False)
            slot.created_by_staff = request.user
            slot.save()
            messages.success(request, 'Time slot created successfully.')
            return redirect('staff_manage_slots')
    else:
        form = TimeSlotForm()

    return render(request, 'booking/manage_slots.html', {
        'form': form,
        'slots': slots,
    })


@login_required
def staff_booking_list_view(request):
    if request.user.role != 'staff':
        messages.error(request, 'Access denied.')
        return redirect('home')

    # Only show bookings for services this staff member created slots for
    staff_services = Service.objects.filter(time_slots__created_by_staff=request.user).distinct()
    bookings = Booking.objects.filter(time_slot__service__in=staff_services).order_by('-created_at')

    return render(request, 'booking/staff_booking_list.html', {
        'bookings': bookings,
    })
    
@login_required
def delete_slot_view(request, slot_id):
    if request.user.role != 'staff':
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    if request.method == 'POST':
        slot = get_object_or_404(TimeSlot, id = slot_id)
        slot.delete()
        messages.success(request, 'Slot deleted.')
    
    return redirect('staff_manage_slots')


@login_required
def add_slot_view(request):
    if request.user.role != 'staff':
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    if request.method == 'POST':
        form = TimeSlotForm(request.POST)
        if form.is_valid():
            slot = form.save(commit = False)
            slot.created_by_staff = request.user
            slot.save()
            messages.success(request, 'Slot added.')
    
    return redirect('staff_manage_slots')
