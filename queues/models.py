from django.db import models
from hospitals.models import Hospital
from appointments.models import Doctor
from django.conf import settings
from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.db.models import F
from django.db import transaction

class Queue(models.Model):
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, null=True, blank=True, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    patient_name = models.CharField(max_length=100, default='  ')
    token_number = models.CharField(max_length=36, unique=True, verbose_name='Add to queue')  # Unique token for each patient in queue (UUID)
    position = models.PositiveIntegerField()  # Position in the queue (1, 2, 3, ...)

    def __str__(self):
        doc = f" (Dr. {self.doctor})" if self.doctor else ''
        return f"{self.patient_name}{doc} - Token: {self.token_number}"


# When a queue entry is removed we need to shift down positions for
# entries that were behind it so positions remain contiguous.
@receiver(post_delete, sender=Queue)
def shift_positions_after_delete(sender, instance, **kwargs):
    # Use a transaction to make the update atomic
    try:
        with transaction.atomic():
            if instance.doctor_id:
                # Shift within the doctor's queue
                Queue.objects.filter(doctor=instance.doctor, position__gt=instance.position).update(position=F('position') - 1)
                # Ensure positions are normalized (1..N) for this doctor
                normalize_positions(doctor=instance.doctor)
            else:
                # Shift within the hospital-wide queue
                Queue.objects.filter(hospital=instance.hospital, position__gt=instance.position).update(position=F('position') - 1)
                # Ensure positions are normalized for this hospital
                normalize_positions(hospital=instance.hospital)
    except Exception:
        # Don't let signal failures crash deletion flow; log if needed
        pass


def normalize_positions(hospital=None, doctor=None):
    """Reindex positions starting from 1 for a given doctor or hospital."""

    try:
        with transaction.atomic():

            if doctor is not None:
                # Normalize only this doctor's queue
                qs = Queue.objects.filter(doctor=doctor).order_by('position', 'id')

            elif hospital is not None:
                # Normalize only hospital-wide queue (doctor is NULL)
                qs = Queue.objects.filter(
                    hospital=hospital,
                    doctor__isnull=True
                ).order_by('position', 'id')

            else:
                return  # nothing to normalize

            # Reassign positions
            for new_pos, q in enumerate(qs, start=1):
                if q.position != new_pos:
                    Queue.objects.filter(pk=q.pk).update(position=new_pos)

    except Exception:
        pass
