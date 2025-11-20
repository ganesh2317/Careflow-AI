from django.db import models
from hospitals.models import Hospital
from appointments.models import Doctor
from django.conf import settings

class Queue(models.Model):
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, null=True, blank=True, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    patient_name = models.CharField(max_length=100, default='Walk-in')
    token_number = models.CharField(max_length=36, unique=True, verbose_name='Add to queue')  # Unique token for each patient in queue (UUID)
    position = models.PositiveIntegerField()  # Position in the queue (1, 2, 3, ...)

    def __str__(self):
        doc = f" (Dr. {self.doctor})" if self.doctor else ''
        return f"{self.patient_name}{doc} - Token: {self.token_number}"
