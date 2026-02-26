from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, ServiceType, Service, TimeSlot, Booking


class UserAdmin(BaseUserAdmin):
    list_display = ('email', 'first_name', 'last_name', 'role', 'is_active')
    list_filter = ('role',)
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Role', {'fields': ('role',)}),
    )


admin.site.register(User, UserAdmin)
admin.site.register(ServiceType)
admin.site.register(Service)
admin.site.register(TimeSlot)
admin.site.register(Booking)