from django.contrib import admin
from .models import Hospital

class HospitalAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return False

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser or hasattr(request.user, 'staff'):
            return qs.filter(name=request.user.username)
        return qs

admin.site.register(Hospital, HospitalAdmin)
