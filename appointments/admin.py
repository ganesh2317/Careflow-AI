from django.contrib import admin
from .models import Doctor, Appointment, DoctorAvailability

class DoctorAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser or hasattr(request.user, 'staff'):
            return qs.filter(hospital__name=request.user.username)
        return qs

class AppointmentAdmin(admin.ModelAdmin):
    exclude = ['user']

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser or hasattr(request.user, 'staff'):
            return qs.filter(doctor__hospital__name=request.user.username)
        return qs

    def save_model(self, request, obj, form, change):
        if not obj.user_id:
            # If the admin form hides the `user` field, assign the current admin user
            # as the appointment user to avoid NOT NULL DB constraint. Adjust if
            # you want admins to create appointments for other users instead.
            obj.user = request.user
        super().save_model(request, obj, form, change)

class DoctorAvailabilityAdmin(admin.ModelAdmin):
    list_display = ['doctor', 'date', 'time']

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser or hasattr(request.user, 'staff'):
            return qs.filter(doctor__hospital__name=request.user.username)
        return qs

admin.site.register(Doctor, DoctorAdmin)
admin.site.register(Appointment, AppointmentAdmin)
admin.site.register(DoctorAvailability, DoctorAvailabilityAdmin)
