from django.contrib import admin
from django.db.models import Max
from .models import Queue
from django import forms
import uuid


class QueueAdminForm(forms.ModelForm):
    class Meta:
        model = Queue
        # expose hospital, doctor and patient_name for admin input; token and position set automatically
        fields = ['hospital', 'doctor', 'patient_name']

    # Make this a class-level field so the admin always renders it
    add_to_queue = forms.IntegerField(
        label='Add to queue',
        required=False,
        initial=0,
        help_text='Enter positive number to add that many, or -1 to remove one.'
    )

    # Read-only display of current queue size for the resolved hospital
    current_queue_size = forms.CharField(
        label='Current Queue Size',
        required=False,
        disabled=True,
        help_text='Current number of people in the resolved hospital queue.'
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add a numeric Add-to-queue input and hide hospital for non-superusers
        # The admin will see a numeric `Add to queue` field; hospital will be filled
        # automatically from the logged-in user's hospital unless the user is superuser.
        # `request` may be attached to the form class by QueueAdmin.get_form.
        request = getattr(self.__class__, 'request', None)

        # add_to_queue is declared on the form class so it's always present; only
        # hide the hospital widget below when appropriate.

        # Always hide the hospital dropdown (we use a numeric Add to queue field instead)
        if 'hospital' in self.fields:
            self.fields['hospital'].widget = forms.HiddenInput()
            # Try to pre-fill hospital from the username mapping when request is attached
            if request is not None:
                try:
                    from hospitals.models import Hospital
                    hosp = Hospital.objects.get(name=request.user.username)
                    self.initial.setdefault('hospital', hosp.pk)
                    # Set the current_queue_size initial value so the form shows it
                    from .models import Queue
                    # If a doctor is provided in initial data, show per-doctor size
                    doc_id = self.initial.get('doctor') or self.data.get('doctor') if hasattr(self, 'data') else None
                    if doc_id:
                        self.initial.setdefault('current_queue_size', str(Queue.objects.filter(doctor_id=doc_id).count()))
                    else:
                        self.initial.setdefault('current_queue_size', str(Queue.objects.filter(hospital=hosp).count()))
                except Exception:
                    # leave current_queue_size empty if mapping fails
                    self.initial.setdefault('current_queue_size', '-')

class QueueAdmin(admin.ModelAdmin):
    list_display = ['patient_name', 'position', 'hospital', 'doctor', 'queue_size']
    # Hide fields that should be set automatically by the admin backend
    exclude = ['position', 'token_number']
    form = QueueAdminForm
    readonly_fields = ['current_queue_size']
    # Ensure the non-model `add_to_queue` field is rendered in the admin form
    fields = ('add_to_queue', 'hospital', 'doctor', 'patient_name', 'current_queue_size')

    def get_form(self, request, obj=None, **kwargs):
        # Attach request to the form class so __init__ can access the user
        form = super().get_form(request, obj, **kwargs)
        setattr(form, 'request', request)
        return form

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # Allow superusers and staff users to see queues for their hospital
        if request.user.is_superuser or request.user.is_staff:
            return qs.filter(hospital__name=request.user.username)
        return qs

    def has_add_permission(self, request):
        # Allow adding if user is superuser or staff; otherwise disallow
        return request.user.is_superuser or request.user.is_staff

    def save_model(self, request, obj, form, change):
        # Process add_to_queue special integer field (batch add/remove)
        add_val = form.cleaned_data.get('add_to_queue')
        try:
            add_count = int(add_val) if add_val not in (None, '') else 0
        except Exception:
            add_count = 0

        # Resolve hospital and doctor: from form if provided (superuser) or from request.user mapping
        hospital = form.cleaned_data.get('hospital')
        doctor = form.cleaned_data.get('doctor')
        if not hospital:
            try:
                from hospitals.models import Hospital
                hospital = Hospital.objects.get(name=request.user.username)
            except Exception:
                hospital = None

        # If add_count is -1 -> remove one from selected hospital's queue
        # If add_count == -1 -> remove one from selected doctor's queue if doctor provided, else from hospital queue
        if add_count == -1:
            if doctor:
                last = Queue.objects.filter(doctor=doctor).order_by('-position').first()
                if last:
                    last.delete()
                    self.message_user(request, f"Removed one person from Dr. {doctor}. New size: {Queue.objects.filter(doctor=doctor).count()}")
                else:
                    self.message_user(request, f"No one in queue for Dr. {doctor} to remove.")
            elif hospital:
                last = Queue.objects.filter(hospital=hospital).order_by('-position').first()
                if last:
                    last.delete()
                    self.message_user(request, f"Removed one person from {hospital}. New size: {Queue.objects.filter(hospital=hospital).count()}")
                else:
                    self.message_user(request, f"No one in queue for {hospital} to remove.")
            return
        # If add_count > 0 -> create that many queue entries for the selected doctor if provided, else for the hospital
        if add_count and add_count > 0:
            # If a patient_name was provided, use it for the first created entry
            first_name = form.cleaned_data.get('patient_name') or 'Walk-in'
            created = 0
            for i in range(add_count):
                q = Queue()
                q.hospital = hospital
                q.doctor = doctor
                q.patient_name = first_name if i == 0 else 'Walk-in'
                # assign position (per-doctor if doctor provided, else per-hospital)
                if doctor:
                    max_position = Queue.objects.filter(doctor=doctor).aggregate(Max('position'))['position__max'] or 0
                elif hospital:
                    max_position = Queue.objects.filter(hospital=hospital).aggregate(Max('position'))['position__max'] or 0
                else:
                    max_position = Queue.objects.all().aggregate(Max('position'))['position__max'] or 0
                q.position = max_position + 1
                # generate a UUID token to ensure global uniqueness
                q.token_number = uuid.uuid4().hex
                q.save()
                created += 1
            target_desc = f"Dr. {doctor}" if doctor else str(hospital)
            self.message_user(request, f"Created {created} queue entries for {target_desc}. New size: {Queue.objects.filter(doctor=doctor).count() if doctor else Queue.objects.filter(hospital=hospital).count()}")
            return

        # Default single-create behavior when add_to_queue is not used
        if not obj.position:
            if obj.doctor_id:
                max_position = Queue.objects.filter(doctor=obj.doctor).aggregate(Max('position'))['position__max'] or 0
            elif hospital:
                max_position = Queue.objects.filter(hospital=hospital).aggregate(Max('position'))['position__max'] or 0
            else:
                max_position = Queue.objects.all().aggregate(Max('position'))['position__max'] or 0
            obj.position = (max_position or 0) + 1

        if not getattr(obj, 'token_number', None):
            obj.token_number = uuid.uuid4().hex

        if not obj.hospital_id and hospital:
            obj.hospital = hospital
        # if doctor provided and not set, set it
        if doctor and not obj.doctor_id:
            obj.doctor = doctor
        super().save_model(request, obj, form, change)

    def queue_size(self, obj):
        if obj.doctor_id:
            return Queue.objects.filter(doctor=obj.doctor).count()
        return Queue.objects.filter(hospital=obj.hospital).count()
    queue_size.short_description = 'Queue Size'

    def current_queue_size(self, obj):
        if obj and obj.hospital_id:
            return Queue.objects.filter(hospital=obj.hospital).count()
        return '-'
    current_queue_size.short_description = 'Current Queue Size'

    def increment_position(self, request, queryset):
        for obj in queryset:
            obj.position += 1
            obj.save()
        self.message_user(request, "Selected queues' positions incremented by 1.")

    def decrement_position(self, request, queryset):
        for obj in queryset:
            if obj.position > 1:
                obj.position -= 1
                obj.save()
        self.message_user(request, "Selected queues' positions decremented by 1.")

    increment_position.short_description = "Increment position by 1"
    decrement_position.short_description = "Decrement position by 1"

    actions = [increment_position, decrement_position]

admin.site.register(Queue, QueueAdmin)
