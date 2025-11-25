from django.contrib import admin
from django.db import connection
from .models import Bed
from .models import BedHold
from hospitals.models import Hospital

class BedAdmin(admin.ModelAdmin):
    list_display = ('hospital', 'occupied', 'available')
    fields = ('hospital', 'occupied', 'available')
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # Avoid touching the DB schema if the column doesn't exist yet
        try:
            with connection.cursor() as cursor:
                cols = [c.name for c in connection.introspection.get_table_description(cursor, 'beds_bed')]
        except Exception:
            cols = []

        has_hospital_col = 'hospital_id' in cols

        # Superusers see all when column exists, otherwise return empty queryset
        if request.user.is_superuser:
            return qs if has_hospital_col else qs.none()
        if hasattr(request.user, 'staff') and has_hospital_col:
            return qs.filter(hospital__name=request.user.username)
        return qs.none()

    def get_form(self, request, obj=None, **kwargs):
        # Dynamically remove `hospital` from the form if DB column not present
        try:
            with connection.cursor() as cursor:
                cols = [c.name for c in connection.introspection.get_table_description(cursor, 'beds_bed')]
        except Exception:
            cols = []

        has_hospital_col = 'hospital_id' in cols

        if not has_hospital_col:
            # remove hospital from fields passed to form
            current_fields = list(getattr(self, 'fields', ()))
            if 'hospital' in current_fields:
                current_fields.remove('hospital')
            kwargs = kwargs.copy()
            kwargs['fields'] = tuple(current_fields)

        return super().get_form(request, obj, **kwargs)

    def save_model(self, request, obj, form, change):
        # If admin (acting as hospital) didn't set hospital, try to assign
        # based on the admin username matching a Hospital.name
        if not obj.hospital_id:
            try:
                obj.hospital = Hospital.objects.get(name=request.user.username)
            except Hospital.DoesNotExist:
                pass
        super().save_model(request, obj, form, change)

admin.site.register(Bed, BedAdmin)


class BedHoldAdmin(admin.ModelAdmin):
    # Show only the user who holds and the time they held it.
    list_display = ('user', 'hold_time')
    actions = ['release_holds']

    def release_holds(self, request, queryset):
        """Release selected holds: increment available and decrement occupied on a Bed record."""
        for hold in queryset:
            # find a Bed record for the hospital to adjust counts
            bed = Bed.objects.filter(hospital=hold.hospital).first()
            if bed:
                # Use F expressions to avoid race conditions
                from django.db.models import F
                bed.available = F('available') + 1
                bed.occupied = F('occupied') - 1
                bed.save()
                bed.refresh_from_db()
        # delete holds after releasing
        queryset.delete()

    release_holds.short_description = 'Release selected bed holds (update counts)'

    def hold_time(self, obj):
        # Display a concise hold timestamp for the admin list view
        try:
            return obj.created_at.strftime('%Y-%m-%d %H:%M:%S')
        except Exception:
            return obj.created_at
    hold_time.short_description = 'Held at'

    def get_queryset(self, request):
        """Limit BedHold rows to the hospital the admin represents (by username) unless superuser."""
        qs = super().get_queryset(request)
        # Avoid touching DB schema if table missing
        try:
            from django.db import connection
            with connection.cursor() as cursor:
                cols = [c.name for c in connection.introspection.get_table_description(cursor, 'beds_bedhold')]
        except Exception:
            cols = []

        has_hospital_col = 'hospital_id' in cols

        if request.user.is_superuser:
            return qs if has_hospital_col else qs.none()

        # If the admin user maps to a Hospital by username, filter to that hospital
        if has_hospital_col:
            try:
                return qs.filter(hospital__name=request.user.username)
            except Exception:
                return qs.none()

        return qs.none()


admin.site.register(BedHold, BedHoldAdmin)
