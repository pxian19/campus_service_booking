from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    ROLE_CHOICES = [
        ('student', 'Student'),
        ('staff', 'Staff'),
    ]

    email = models.EmailField(unique = True)
    role = models.CharField(max_length = 10, choices = ROLE_CHOICES, default = 'student')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.role})"


class ServiceType(models.Model):
    name = models.CharField(max_length = 50)
    icon = models.CharField(max_length = 50, blank = True)
    color = models.CharField(max_length = 20, blank = True)

    def __str__(self):
        return self.name
    
    
class Service(models.Model):
    service_type = models.ForeignKey(ServiceType, on_delete = models.CASCADE, related_name = 'services')
    name = models.CharField(max_length = 100)
    location = models.CharField(max_length = 100)
    is_active = models.BooleanField(default = True)

    def __str__(self):
        return f"{self.name} ({self.service_type.name})"


class TimeSlot(models.Model):
    service = models.ForeignKey(Service, on_delete = models.CASCADE, related_name = 'time_slots')
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_available = models.BooleanField(default = True)
    created_by_staff = models.ForeignKey(
        User, on_delete = models.SET_NULL, null = True, blank = True,
        limit_choices_to = {'role': 'staff'}, related_name = 'created_time_slots'
    )

    class Meta:
        ordering = ['date', 'start_time']
        unique_together = ['service', 'date', 'start_time', 'end_time']

    def __str__(self):
        return f"{self.service.name} | {self.date} {self.start_time} - {self.end_time}"


class Booking(models.Model):
    STATUS_CHOICES = [
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
    ]

    user = models.ForeignKey(User, on_delete = models.CASCADE, related_name = 'bookings')
    time_slot = models.ForeignKey(TimeSlot, on_delete = models.CASCADE, related_name = 'bookings')
    notes = models.TextField(blank = True)
    status = models.CharField(max_length = 10, choices = STATUS_CHOICES, default = 'confirmed')
    created_at = models.DateTimeField(auto_now_add = True)
    cancelled_at = models.DateTimeField(null = True, blank = True)
    confirmation_email_sent = models.BooleanField(default = False)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.email} | {self.time_slot} [{self.status}]"