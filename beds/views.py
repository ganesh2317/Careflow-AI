from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Sum, F
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.contrib import messages

from .models import Bed
from hospitals.models import Hospital


def track_beds(request, hospital_id):
    hospital = get_object_or_404(Hospital, id=hospital_id)
    beds = Bed.objects.filter(hospital=hospital)

    # beds model stores counts per record; aggregate sums across records
    available_sum = beds.aggregate(total_available=Sum('available'))['total_available'] or 0
    occupied_sum = beds.aggregate(total_occupied=Sum('occupied'))['total_occupied'] or 0

    return render(request, 'beds/track.html', {'available': available_sum, 'occupied': occupied_sum, 'hospital': hospital})


@login_required
def hold_bed(request, hospital_id):
    if request.method != 'POST':
        return redirect('beds:track_beds', hospital_id=hospital_id)

    hospital = get_object_or_404(Hospital, id=hospital_id)

    # Atomically find a Bed with available > 0 and decrement it.
    with transaction.atomic():
        bed = Bed.objects.select_for_update().filter(hospital=hospital, available__gt=0).order_by('-available').first()
        if not bed:
            messages.error(request, 'No beds available to hold.')
            return redirect('beds:track_beds', hospital_id=hospital_id)

        bed.available = F('available') - 1
        bed.occupied = F('occupied') + 1
        bed.save()
        bed.refresh_from_db()

    messages.success(request, 'Bed held successfully.')
    return redirect('beds:track_beds', hospital_id=hospital_id)
