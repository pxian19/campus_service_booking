from django.urls import path
from . import views

# URL patterns for booking app
urlpatterns = [
    # Home page: shows different home templates based on user role (student/staff)
    path('', views.home_view, name='home'),
    # User registration page (create a new account)
    path('register/', views.register_view, name='register'),
    # User login page (email + password)
    path('login/', views.login_view, name='login'),
    # User logout
    path('logout/', views.logout_view, name='logout'),
    
    # Student: browse services
    path('services/', views.service_list_view, name='service_list'),
    path('services/<int:service_id>/slots/', views.slot_list_view, name='slot_list'),
    path('services/type/<int:type_id>/', views.slots_by_type_view, name='slots_by_type'),

    # Student: bookings
    path('book/<int:slot_id>/', views.create_booking_view, name='create_booking'),
    path('book/<int:slot_id>/confirm/', views.confirm_booking_view, name='confirm_booking'),
    path('my-bookings/', views.my_bookings_view, name='my_bookings'),
    path('cancel-booking/<int:booking_id>/', views.cancel_booking_view, name='cancel_booking'),

    # Staff
    path('staff/create-service/', views.staff_create_service_view, name='staff_create_service'),
    path('staff/slots/', views.staff_manage_slots_view, name='staff_manage_slots'),
    path('staff/bookings/', views.staff_booking_list_view, name='staff_booking_list'),
    path('staff/slots/delete/<int:slot_id>/', views.delete_slot_view, name='delete_slot'),
    path('staff/slots/add/', views.add_slot_view, name='add_slot'),
]