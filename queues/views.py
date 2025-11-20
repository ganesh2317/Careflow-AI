from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Max
from .models import Queue
from hospitals.models import Hospital
import uuid


def book_token(request, hospital_id):
    # Show doctor selection page for the hospital. Booking happens after doctor selection.
    hospital = get_object_or_404(Hospital, id=hospital_id)
    doctors = hospital.doctor_set.all()
    return render(request, 'queues/select_doctor.html', {'hospital': hospital, 'doctors': doctors})


def book_token_doctor(request, doctor_id):
    from appointments.models import Doctor
    doctor = get_object_or_404(Doctor, id=doctor_id)
    hospital = doctor.hospital
    # Assign next position for this doctor
    max_position = Queue.objects.filter(doctor=doctor).aggregate(Max('position'))['position__max'] or 0
    next_pos = max_position + 1
    if request.user.is_authenticated:
        patient_name = request.user.get_full_name() or request.user.username
    else:
        patient_name = 'Walk-in'
    token_number = uuid.uuid4().hex
    queue_entry = Queue.objects.create(hospital=hospital, doctor=doctor, patient_name=patient_name, token_number=token_number, position=next_pos)
    if request.user.is_authenticated:
        queue_entry.user = request.user
        queue_entry.save()
    # Render token confirmation and provide Track Queue button on same page
    return redirect('queues:token_confirm', token_id=queue_entry.id)

def token_confirm(request, token_id):
    token = get_object_or_404(Queue, id=token_id)
    return render(request, 'queues/token_confirm.html', {'token': token})

def query_token(request, token_id):
    token = get_object_or_404(Queue, id=token_id, user=request.user)
    return render(request, 'queues/query.html', {'token': token})

def manage_queue(request, hospital_id):
    hospital = get_object_or_404(Hospital, id=hospital_id)
    queues = Queue.objects.filter(hospital=hospital).order_by('position')
    return render(request, 'queues/manage.html', {'hospital': hospital, 'queues': queues})

def increment_queue(request, hospital_id):
    hospital = get_object_or_404(Hospital, id=hospital_id)
    # AI to increment queue positions
    queues = Queue.objects.filter(hospital=hospital).order_by('position')
    for queue in queues:
        queue.position += 1
        queue.save()
    return redirect('queues:manage_queue', hospital_id=hospital_id)

def decrement_queue(request, hospital_id):
    hospital = get_object_or_404(Hospital, id=hospital_id)
    # AI to decrement queue positions
    queues = Queue.objects.filter(hospital=hospital).order_by('position')
    for queue in queues:
        if queue.position > 1:
            queue.position -= 1
            queue.save()
    return redirect('queues:manage_queue', hospital_id=hospital_id)
