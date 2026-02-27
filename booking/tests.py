from django.test import TestCase, Client
from django.urls import reverse
from .models import User, ServiceType, Service, TimeSlot, Booking
from datetime import date, time


# Test User model and email validation
class UserModelTest(TestCase):
    
    # Create a student user
    def test_create_student(self):
        user = User.objects.create_user(
            username='teststudent',
            email='test@student.gla.ac.uk',
            password='Testpass123!',
            first_name='Test',
            last_name='Student',
            role='student',
        )
        # Check saved values are correct
        self.assertEqual(user.role, 'student')
        self.assertEqual(user.email, 'test@student.gla.ac.uk')

    # Create a staff user
    def test_create_staff(self):
        user = User.objects.create_user(
            username='teststaff',
            email='test@gla.ac.uk',
            password='Testpass456!',
            first_name='Test',
            last_name='Staff',
            role='staff',
        )
        # Check role is staff
        self.assertEqual(user.role, 'staff')


# Test ServiceType and Service models
class ServiceModelTest(TestCase):

    def setUp(self):
        self.service_type = ServiceType.objects.create(
            name='Library', icon='book', color='#FFB6C1'
        )
        self.service = Service.objects.create(
            service_type=self.service_type,
            name='Library A1',
            location='Main Library Building',
            is_active=True,
        )

    def test_service_type_creation(self):
        self.assertEqual(self.service_type.name, 'Library')

    def test_service_belongs_to_type(self):
        self.assertEqual(self.service.service_type, self.service_type)

    def test_service_str(self):
        self.assertEqual(str(self.service), 'Library A1 (Library)')


# Test TimeSlot model and uniqueness
class TimeSlotModelTest(TestCase):

    def setUp(self):
        service_type = ServiceType.objects.create(name='Study Room')
        self.service = Service.objects.create(
            service_type=service_type,
            name='Study Room B419',
            location='Joseph Black Building',
        )
        
        # Create one slot for testing
        self.slot = TimeSlot.objects.create(
            service=self.service,
            date=date(2026, 3, 10),
            start_time=time(9, 0),
            end_time=time(9, 30),
        )

    def test_slot_is_available_by_default(self):
        self.assertTrue(self.slot.is_available)
    
    # Creating the same slot again should break unique_together constraint
    def test_no_duplicate_slots(self):
        from django.db import IntegrityError
        with self.assertRaises(IntegrityError):
            TimeSlot.objects.create(
                service=self.service,
                date=date(2026, 3, 10),
                start_time=time(9, 0),
                end_time=time(9, 30),
            )


# Test Booking model
class BookingModelTest(TestCase):

    def setUp(self):
        # Create a student user
        self.user = User.objects.create_user(
            username='bookuser',
            email='book@student.gla.ac.uk',
            password='TestPass123!',
            first_name='Book',
            last_name='User',
            role='student',
        )
        
        # Create a service and a time slot to book
        service_type = ServiceType.objects.create(name='Library')
        service = Service.objects.create(
            service_type=service_type,
            name='Library A1',
            location='Main Library',
        )
        self.slot = TimeSlot.objects.create(
            service=service,
            date=date(2026, 3, 10),
            start_time=time(10, 0),
            end_time=time(10, 30),
        )
    # When created, booking status should default to 'confirmed'
    def test_booking_default_status(self):
        booking = Booking.objects.create(
            user=self.user, time_slot=self.slot
        )
        self.assertEqual(booking.status, 'confirmed')

    # Simulate cancelling a booking
    def test_booking_cancel(self):
        from django.utils import timezone
        booking = Booking.objects.create(
            user=self.user, time_slot=self.slot
        )
        booking.status = 'cancelled'
        booking.cancelled_at = timezone.now()
        booking.save()
        
        # Check cancellation fields saved correctly
        self.assertEqual(booking.status, 'cancelled')
        self.assertIsNotNone(booking.cancelled_at)


# Test registration with valid and invalid emails
class RegistrationTest(TestCase):

    def test_register_valid_email(self):
        client = Client()
        response = client.post(reverse('register'), {
            'email': 'new@student.gla.ac.uk',
            'username': 'newstudent',
            'first_name': 'New',
            'last_name': 'Student',
            'role': 'student',
            'password1': 'PassPass123!',
            'password2': 'PassPass123!',
        })
        
        # After registration, user should exist in database
        self.assertEqual(User.objects.filter(email='new@student.gla.ac.uk').count(), 1)

    def test_register_invalid_email(self):
        client = Client()
        response = client.post(reverse('register'), {
            'email': 'test@gmail.com',
            'username': 'Gmail',
            'first_name': 'Gamil',
            'last_name': 'User',
            'role': 'student',
            'password1': 'PassPass456!',
            'password2': 'PassPass456!',
        })
        
        # User should NOT be created
        self.assertEqual(User.objects.filter(email='test@gmail.com').count(), 0)


# Test login and role-based redirect
class LoginTest(TestCase):

    def setUp(self):
        self.student = User.objects.create_user(
            username='loginstudent',
            email='login@student.gla.ac.uk',
            password='TestPass123!',
            first_name='Login',
            last_name='Student',
            role='student',
        )

    def test_login_success(self):
        client = Client()
        response = client.post(reverse('login'), {
            'email': 'login@student.gla.ac.uk',
            'password': 'TestPass123!',
        })
        
        # Successful login should redirect to home page
        self.assertRedirects(response, reverse('home'))

    def test_login_wrong_password(self):
        client = Client()
        response = client.post(reverse('login'), {
            'email': 'login@student.gla.ac.uk',
            'password': 'WrongPass!',
        })
        self.assertEqual(response.status_code, 200)
