from django.db import models
from django.contrib.auth.models import User
from hospitals.models import Hospital

class Bed(models.Model):
    hospital = models.ForeignKey(Hospital, null=True, blank=True, on_delete=models.CASCADE)
    # Keep counts for occupied/available beds per hospital
    occupied = models.PositiveIntegerField(default=0, help_text="Number of occupied beds")
    available = models.PositiveIntegerField(default=0, help_text="Number of available beds")

    def __str__(self):
        return f"Beds ({self.hospital}) - Occupied: {self.occupied}, Available: {self.available}"

class BedHold(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE)
    bed = models.ForeignKey('Bed', null=True, blank=True, on_delete=models.SET_NULL)
    hold_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Bed held by {self.user.username} at {self.hospital.name} on {self.hold_time.strftime('%Y-%m-%d %H:%M:%S')}"
