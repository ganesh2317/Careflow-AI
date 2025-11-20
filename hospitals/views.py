from django.shortcuts import render, get_object_or_404
from .models import Hospital
from django.contrib.auth.models import User
from appointments.models import Appointment
from beds.models import Bed

def hospital_list(request):
    hospitals = Hospital.objects.all()
    query = request.GET.get('q')
    if query:
        hospitals = hospitals.filter(name__icontains=query)

    hospital_list = [{'name': h.name, 'id': h.id} for h in hospitals]

    # Only append superuser-created hospitals when not searching, to avoid
    # returning unrelated results during a query.
    if not query:
        superusers = User.objects.filter(is_superuser=True)
        for user in superusers:
            hospital, created = Hospital.objects.get_or_create(name=user.username)
            # ensure we don't duplicate entries
            if not any(h['id'] == hospital.id for h in hospital_list):
                hospital_list.append({'name': hospital.name, 'id': hospital.id})

    return render(request, 'hospitals/hospital_list.html', {'hospitals': hospital_list, 'query': query})

def hospital_detail(request, hospital_id):
    hospital = get_object_or_404(Hospital, id=hospital_id)
    # Check if hospital has any beds, doctors, etc. added by admin
    # Bed model may or may not have a hospital FK; handle both cases.
    try:
        # if Bed has hospital relation, filter by hospital
        has_beds = Bed.objects.filter(hospital=hospital).exists()
    except Exception:
        # fallback to any Bed records
        has_beds = Bed.objects.exists()
    has_doctors = hospital.doctor_set.exists()
    has_queues = hospital.queue_set.exists()
    # Build a list of doctors with their queue sizes
    doctors = []
    if has_doctors:
        for d in hospital.doctor_set.all():
            from queues.models import Queue
            size = Queue.objects.filter(doctor=d).count()
            doctors.append({'id': d.id, 'name': str(d), 'queue_size': size})
    # Appointments are related through doctors, so check if there are appointments for doctors in this hospital
    has_appointments = Appointment.objects.filter(doctor__hospital=hospital).exists()
    return render(request, 'hospitals/hospital_detail.html', {
        'hospital': hospital,
        'has_beds': has_beds,
        'has_doctors': has_doctors,
        'has_queues': has_queues,
        'has_appointments': has_appointments
        , 'doctors': doctors
    })
