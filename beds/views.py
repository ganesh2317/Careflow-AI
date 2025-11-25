from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Sum, F
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.contrib import messages

from .models import Bed, BedHold
from hospitals.models import Hospital


def track_beds(request, hospital_id):
    hospital = get_object_or_404(Hospital, id=hospital_id)
    beds = Bed.objects.filter(hospital=hospital)

    # beds model stores counts per record; aggregate sums across records
    available_sum = beds.aggregate(total_available=Sum('available'))['total_available'] or 0
    occupied_sum = beds.aggregate(total_occupied=Sum('occupied'))['total_occupied'] or 0

    # Get bed holds for this hospital with user prefetch for optimization
    bed_holds = BedHold.objects.filter(hospital=hospital).select_related('user')

    return render(
        request,
        'beds/track.html',
        {
            'available': available_sum,
            'occupied': occupied_sum,
            'hospital': hospital,
            'bed_holds': bed_holds
        }
    )


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

        # Create BedHold record for this user, hospital, and bed
        BedHold.objects.create(user=request.user, hospital=hospital, bed=bed)

    messages.success(request, 'Bed held successfully.')
    return redirect('beds:track_beds', hospital_id=hospital_id)


@login_required
def release_bed_hold(request, hold_id):
    # Allow hospital admin or superuser to delete the bed hold record (release the bed)
    hold = get_object_or_404(BedHold, id=hold_id)
    hospital = hold.hospital

    # More precise permission check: superuser or staff of hospital (improve from user.staff only)
    if not request.user.is_superuser:
        # Assuming staff users have a hospital relation, check if user is staff of this hospital
        # We also keep original user.staff attribute for backward compatibility
        user_is_hospital_staff = False
        if hasattr(request.user, 'staff') and request.user.staff:
            # Assuming user model or staff profile has hospital relation for permission
            if hasattr(request.user, 'staff_hospital_id'):
                if request.user.staff_hospital_id == hospital.id:
                    user_is_hospital_staff = True
            # fallback: if username same as hospital name, still allow (can be improved)
            elif request.user.username == hospital.name:
                user_is_hospital_staff = True

        if not user_is_hospital_staff:
            messages.error(request, 'You do not have permission to release this bed hold.')
            return redirect('beds:track_beds', hospital_id=hospital.id)


    with transaction.atomic():
        # Increment available bed count and decrement occupied count on exact bed held
        bed = hold.bed
        if bed:
            bed = Bed.objects.select_for_update().get(id=bed.id)
            bed.available = F('available') + 1
            bed.occupied = F('occupied') - 1
            bed.save()
            bed.refresh_from_db()

        hold.delete()

    messages.success(request, f'Bed hold by user "{hold.user.username}" released successfully.')
    return redirect('beds:track_beds', hospital_id=hospital.id)
