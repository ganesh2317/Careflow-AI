from django.shortcuts import render, get_object_or_404, redirect
from .models import Doctor, Appointment, DoctorAvailability
from hospitals.models import Hospital
from django.contrib import messages
from django.contrib.auth.decorators import login_required

@login_required
def book_appointment(request, hospital_id):
    hospital = get_object_or_404(Hospital, id=hospital_id)
    doctors = Doctor.objects.filter(hospital=hospital).exclude(date__isnull=True, time__isnull=True)
    if request.method == 'POST':
        doctor_id = request.POST.get('doctor_id')
        if doctor_id:
            doctor = get_object_or_404(Doctor, id=doctor_id, hospital=hospital)
            # Check if already booked
            if not Appointment.objects.filter(doctor=doctor, date=doctor.date, time=doctor.time).exists():
                Appointment.objects.create(user=request.user, doctor=doctor, date=doctor.date, time=doctor.time)
                messages.success(request, 'Your appointment has been scheduled.')
                return redirect('hospitals:hospital_detail', hospital_id=hospital_id)
            else:
                messages.error(request, 'This slot is already booked.')
        else:
            messages.error(request, 'Invalid request.')
    return render(request, 'appointments/book.html', {'doctors': doctors})
