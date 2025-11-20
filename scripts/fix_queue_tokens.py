import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hospital_management.settings')
django.setup()
from queues.models import Queue

print('Updating token_number for existing Queue rows to unique values (using id).')
for q in Queue.objects.all():
    q.token_number = str(q.id)
    q.save()
print('Done.')
