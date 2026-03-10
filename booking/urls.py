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
    path('services/', views.service_list_view, name='service_list'),
    path('services/<int:service_id>/slots/', views.slot_list_view, name='slot_list'),
    path('book/<int:slot_id>/', views.create_booking_view, name='create_booking'),
]