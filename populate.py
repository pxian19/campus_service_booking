import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'campus_service_booking.settings')
django.setup()

from datetime import date, time, timedelta
from booking.models import ServiceType, Service, TimeSlot, User


def populate():
    # Clear existing data to avoid duplicates
    TimeSlot.objects.all().delete()
    Service.objects.all().delete()
    ServiceType.objects.all().delete()

    print('Creating service types...')

    # Create 5 service types matching design specification
    service_types = {
        'Library': {'icon': 'book', 'color': '#FFB6C1'},
        'Study Room': {'icon': 'home', 'color': '#FFD4A3'},
        'Counselling': {'icon': 'chat', 'color': '#B5E8B5'},
        'Repair': {'icon': 'wrench', 'color': '#A3C4F3'},
        'Tutor': {'icon': 'graduation-cap', 'color': '#D4A3F3'},
    }

    created_types = {}
    for name, attrs in service_types.items():
        st = ServiceType.objects.create(name=name, icon=attrs['icon'], color=attrs['color'])
        created_types[name] = st
        print(f'  Created: {name}')

    print('Creating services...')

    # Create Service records under each ServiceType
    services_data = {
        'Library': [
            {'name': 'Library A1', 'location': 'Main Library Building'},
            {'name': 'Library B2', 'location': 'James Watt Building'},
        ],
        'Study Room': [
            {'name': 'Study Room B419', 'location': 'Joseph Black Building'},
            {'name': 'Study Room C301', 'location': 'Boyd Orr Building'},
        ],
        'Counselling': [
            {'name': 'Dr. Smith', 'location': 'Student Welfare Office'},
            {'name': 'Dr. Johnson', 'location': 'Student Welfare Office'},
        ],
        'Repair': [
            {'name': 'IT Repair Desk', 'location': 'IT Support Centre'},
        ],
        'Tutor': [
            {'name': 'Academic Advisor', 'location': 'Student Services Building'},
            {'name': 'Programming Tutor', 'location': 'Computing Science Building'},
        ],
    }

    # Store created Service objects
    created_services = {}
    for type_name, services in services_data.items():
        created_services[type_name] = []
        for s in services:
            service = Service.objects.create(
                service_type=created_types[type_name],
                name=s['name'],
                location=s['location'],
                is_active=True,
            )
            created_services[type_name].append(service)
            print(f'  Created: {service.name}')

    print('Creating time slots...')

    # Prepare date range for the next 7 days
    today = date.today()
    week_dates = [today + timedelta(days=i) for i in range(7)]
    
    # Weekdays only (Monday - Friday) used for Repair slots
    weekday_dates = [d for d in week_dates if d.weekday() < 5]

    # Generate slots for Library & Study Room: every day 8:00-22:00, 30min slots
    for type_name in ['Library', 'Study Room']:
        for service in created_services[type_name]:
            for d in week_dates:
                hour = 8
                minute = 0
                while hour < 22:
                    
                    # Slot start time
                    start = time(hour, minute)
                    
                    # Slot end time (start + 30 minutes)
                    end_minute = minute + 30
                    end_hour = hour
                    if end_minute == 60:
                        end_minute = 0
                        end_hour += 1
                    end = time(end_hour, end_minute)
                    
                    # Create the slot record in database
                    TimeSlot.objects.create(
                        service=service, date=d,
                        start_time=start, end_time=end,
                    )
                    
                    # Move to next 30-minute slot
                    minute += 30
                    if minute == 60:
                        minute = 0
                        hour += 1
            print(f'  Slots created for: {service.name}')

    # Generate slots for Repair: weekdays 9:00-18:00, 30min slots
    for service in created_services['Repair']:
        for d in weekday_dates:
            hour = 9
            minute = 0
            while hour < 18:
                start = time(hour, minute)
                end_minute = minute + 30
                end_hour = hour
                if end_minute == 60:
                    end_minute = 0
                    end_hour += 1
                end = time(end_hour, end_minute)
                TimeSlot.objects.create(
                    service=service, date=d,
                    start_time=start, end_time=end,
                )
                minute += 30
                if minute == 60:
                    minute = 0
                    hour += 1
        print(f'  Slots created for: {service.name}')

    # Counselling & Tutor: no auto-generated slots (created by staff)
    print('  Counselling & Tutor: slots to be created by staff')

    # Create demo accounts for testing
    print('Creating demo accounts...')

    if not User.objects.filter(email='student@student.gla.ac.uk').exists():
        User.objects.create_user(
            username='demo_student',
            email='student@student.gla.ac.uk',
            password='DemoPass123!',
            first_name='Demo',
            last_name='Student',
            role='student',
        )
        print('  Created: demo student account')

    if not User.objects.filter(email='staff@gla.ac.uk').exists():
        User.objects.create_user(
            username='demo_staff',
            email='staff@gla.ac.uk',
            password='DemoPass123!',
            first_name='Demo',
            last_name='Staff',
            role='staff',
        )
        print('  Created: demo staff account')

    print('Population complete!')


if __name__ == '__main__':
    populate()
    
    
    