from .models import Queue
from django.db.models import Q


def my_tokens(request):
    """Return tokens for the logged-in user.

    We match by explicit `user` FK when present. For tokens created before
    the `user` FK existed, also match by `patient_name` equal to the user's
    username or full name as a fallback so users see tokens they booked earlier.
    """
    if request.user.is_authenticated:
        uname = request.user.username
        full = request.user.get_full_name() or ''
        tokens = Queue.objects.filter(
            Q(user=request.user) | Q(patient_name__iexact=uname) | Q(patient_name__iexact=full)
        ).select_related('hospital')
        return {
            'my_tokens': [
                {
                    'id': t.id,
                    'position': t.position,
                    'token_number': t.token_number,
                    'hospital_name': t.hospital.name if t.hospital else '',
                }
                for t in tokens
            ]
        }
    return {'my_tokens': []}
