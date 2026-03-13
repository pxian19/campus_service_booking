from django.contrib import admin
from django.urls import path, include

# Main URL configuration, connects admin and booking app
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('booking.urls')),
    
]