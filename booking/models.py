from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """Custom user model:
    - Use email as the login identifier
    - Store role (student/staff) for role-based access control
    """
    ROLE_CHOICES = [
        ('student', 'Student'),
        ('staff', 'Staff'),
    ]
    
    # Email must be unique because we use it to log in
    email = models.EmailField(unique = True)
   
    # Role controls access to staff-only features
    role = models.CharField(max_length = 10, choices = ROLE_CHOICES, default = 'student')
   
    # Make email as the primary login field instead of username
    USERNAME_FIELD = 'email'
   
    # These fields are still required when creating a superuser via createsuperuser
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.role})"


class ServiceType(models.Model):
    """High-level category of services (e.g., Library / Study Room / Repair)"""
    name = models.CharField(max_length = 50)
   
    # Optional UI fields used by templates (icons/colors)
    icon = models.CharField(max_length = 50, blank = True)
    color = models.CharField(max_length = 20, blank = True)

    def __str__(self):
        return self.name
    
    
class Service(models.Model):
    """A specific service instance under a ServiceType (e.g., Study Room B419)"""
    service_type = models.ForeignKey(ServiceType, on_delete = models.CASCADE, related_name = 'services')
    name = models.CharField(max_length = 100)
    location = models.CharField(max_length = 100)
    is_active = models.BooleanField(default = True)

    def __str__(self):
        return f"{self.name} ({self.service_type.name})"


class TimeSlot(models.Model):
    """A bookable time slot for a service"""
    service = models.ForeignKey(Service, on_delete = models.CASCADE, related_name = 'time_slots')
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    
    # Used to quickly indicate if a slot can be booked
    is_available = models.BooleanField(default = True)
    
    # Track which staff member created this slot
    created_by_staff = models.ForeignKey(
        User, on_delete = models.SET_NULL, null = True, blank = True,
        limit_choices_to = {'role': 'staff'}, related_name = 'created_time_slots'
    )

    class Meta:
        # Default ordering for display
        ordering = ['date', 'start_time']
        # Prevent duplicate slots for the same service and exact time range
        unique_together = ['service', 'date', 'start_time', 'end_time']

    def __str__(self):
        return f"{self.service.name} | {self.date} {self.start_time} - {self.end_time}"


class Booking(models.Model):
    """A user's booking for a specific time slot"""
    STATUS_CHOICES = [
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
    ]

    user = models.ForeignKey(User, on_delete = models.CASCADE, related_name = 'bookings')
    time_slot = models.ForeignKey(TimeSlot, on_delete = models.CASCADE, related_name = 'bookings')
    
    # Optional notes entered by the user during booking
    notes = models.TextField(blank = True)
    status = models.CharField(max_length = 10, choices = STATUS_CHOICES, default = 'confirmed')
    
    # Timestamps for audit and UI display
    created_at = models.DateTimeField(auto_now_add = True)
    cancelled_at = models.DateTimeField(null = True, blank = True)
    
    # Track whether a confirmation email was successfully sent
    confirmation_email_sent = models.BooleanField(default = False)

    class Meta:
        # Show newest bookings first
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.email} | {self.time_slot} [{self.status}]"