from django.db import models
from hospitals.models import Hospital


class Bed(models.Model):
    hospital = models.ForeignKey(Hospital, null=True, blank=True, on_delete=models.CASCADE)
    # Keep counts for occupied/available beds per hospital
    occupied = models.PositiveIntegerField(default=0, help_text="Number of occupied beds")
    available = models.PositiveIntegerField(default=0, help_text="Number of available beds")

    def __str__(self):
        return f"Beds ({self.hospital}) - Occupied: {self.occupied}, Available: {self.available}"
