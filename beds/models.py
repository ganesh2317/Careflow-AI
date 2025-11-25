from django.db import models
from hospitals.models import Hospital
from django.conf import settings
from django.utils import timezone


class Bed(models.Model):
    hospital = models.ForeignKey(Hospital, null=True, blank=True, on_delete=models.CASCADE)
    # Keep counts for occupied/available beds per hospital
    occupied = models.PositiveIntegerField(default=0, help_text="Number of occupied beds")
    available = models.PositiveIntegerField(default=0, help_text="Number of available beds")

    def __str__(self):
        return f"Beds ({self.hospital}) - Occupied: {self.occupied}, Available: {self.available}"


class BedHold(models.Model):
    """Represents a single held bed reservation by a user for a hospital.

    Storing this separately keeps history and lets admin release holds explicitly.
    """
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Hold: {self.hospital} by {self.user or 'anonymous'} at {self.created_at}"
