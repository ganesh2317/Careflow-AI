from django.db import models

class Hospital(models.Model):
    name = models.CharField(max_length=100)
    address = models.TextField()
    # Add other fields as needed

    def __str__(self):
        return self.name
