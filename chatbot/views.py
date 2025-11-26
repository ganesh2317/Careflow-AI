import os
import google.generativeai as genai
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.db.models import Sum
from queues.models import Queue
from beds.models import BedHold
from appointments.models import Appointment, Doctor
from hospitals.models import Hospital
from beds.models import Bed
# Try to import the TF-based intent classifier (optional)
try:
    from .intent_model import predict_intent
    INTENT_MODEL_AVAILABLE = True
except Exception:
    predict_intent = None
    INTENT_MODEL_AVAILABLE = False

# Configure Gemini API
genai.configure(api_key='AIzaSyATwaNkpl9jECLM6GE1w8U7ncw4bRW_ksw') # Replace with actual key or set in env


def chatbot_view(request, token_id):
    # Allow anonymous users to access chatbot for their token
    token = get_object_or_404(Queue, id=token_id)
    return render(request, 'chatbot/chat.html', {'token': token, 'token_id': token_id})


def general_chat_view(request):
    return render(request, 'chatbot/general_chat.html')


def waiting_time(request, token_id):
    token = get_object_or_404(Queue, id=token_id)
    position = token.position
    avg_time = 15  # minutes per person (simple heuristic)
    waiting_minutes = position * avg_time
    response = f"Your estimated waiting time is {waiting_minutes} minutes."
    return JsonResponse({'response': response})


def queue_status(request, token_id):
    token = get_object_or_404(Queue, id=token_id)
    response = f"Your current queue position is {token.position}."
    return JsonResponse({'response': response})

<<<<<<< HEAD
@csrf_exempt
@require_POST
def chat_message(request, token_id=None):
    message = request.POST.get('message', '').strip()

=======

import logging

logger = logging.getLogger(__name__)

@csrf_exempt
@require_POST
def chat_message(request, token_id=None):
    message = request.POST.get('message', '')
    hospital_id = request.POST.get('hospital_id') or request.GET.get('hospital_id')
>>>>>>> b73893c741ba2eacf891890fb9034369e7c8cf1c
    if not message:
        return JsonResponse({'response': 'Please enter a message.'})
    # Normalize message for simple keyword intent matching
    text = message.lower()

<<<<<<< HEAD
    # Fetch hospital context
    hospital_data = ""
    try:
        token = Queue.objects.select_related('hospital', 'doctor').get(id=token_id)

        hospital = token.hospital
        doctor = token.doctor

        hospital_data = f"""
You are an AI assistant for the hospital: {hospital.name}.

Hospital Details:
- Name: {hospital.name}
- Address: {hospital.address if hasattr(hospital, 'address') else 'Not available'}

Doctor Assigned:
- Doctor Name: {doctor.name if doctor else 'Not assigned'}
- Specialization: {doctor.specialization if doctor else 'N/A'}

Queue Status:
- Position: {token.position}
"""

    except:
        hospital_data = "Hospital details not found."

    system_rules = """
SYSTEM RULES:
- You are an AI assistant for a hospital management system.
- Answer questions based only on the provided hospital data and system context.
- Do not provide medical advice, diagnoses, or treatment recommendations.
- Focus on hospital services such as appointments, queue status, bed availability, and general hospital information.
- Maintain patient privacy and do not disclose sensitive information.
- If the question is outside the scope of hospital services or requires professional medical help, politely redirect the user to consult hospital staff or appropriate services.
- Keep responses clear, concise, and helpful.
- If information is not available in the provided data, state that you do not have that information.
"""

    final_prompt = f"""
{system_rules}
HOSPITAL INFO:
{hospital_data}

USER QUESTION:
{message}

Your response:
"""

    try:
        model = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content(final_prompt)
        reply = response.text or "I could not generate a response."
    except Exception as e:
        reply = f"Error: {str(e)}"
=======
    # If a TensorFlow intent model exists and a prediction is confident,
    # use it to route to the proper system handler. Threshold is conservative.
    predicted_intent = None
    predicted_conf = 0.0
    if INTENT_MODEL_AVAILABLE and predict_intent is not None:
        try:
            predicted_intent, predicted_conf = predict_intent(message)
        except Exception:
            predicted_intent, predicted_conf = None, 0.0

    # If model predicts a system intent with confidence > 0.6, map to handlers
    if predicted_intent and predicted_conf and predicted_conf >= 0.6:
        intent = predicted_intent
        # map model intent names to existing handling paths
        if intent == 'waiting_time' or intent == 'queue_position':
            # reuse existing handler logic
            if token:
                position = token.position
                avg_time = 10
                mins = position * avg_time
                return JsonResponse({'response': f'Your estimated waiting time is {mins} minutes (position {position}).'})
            return JsonResponse({'response': 'Open chat from your token page and I can show your waiting time.'})
        if intent == 'who_is_my_doctor':
            if token and getattr(token, 'doctor', None):
                d = token.doctor
                return JsonResponse({'response': f'Your doctor is {d.name} ({d.specialty}).'})
            user = token.user if token and getattr(token, 'user', None) else getattr(request, 'user', None)
            if user and getattr(user, 'is_authenticated', False):
                appt = Appointment.objects.filter(user=user).order_by('date', 'time').first()
                if appt:
                    d = appt.doctor
                    return JsonResponse({'response': f'Your next appointment is with {d.name} ({d.specialty}) on {appt.date} at {appt.time}.'})
                return JsonResponse({'response': 'I could not find a doctor on your upcoming appointments.'})
            return JsonResponse({'response': 'I could not determine your doctor. Open chat from your token page or log in.'})
        if intent == 'appointments':
            user = token.user if token and getattr(token, 'user', None) else getattr(request, 'user', None)
            if user and user.is_authenticated:
                appts = Appointment.objects.filter(user=user).order_by('date', 'time')
                if not appts.exists():
                    return JsonResponse({'response': 'You have no upcoming appointments.'})
                lines = [f"{a.doctor.name} on {a.date} at {a.time}" for a in appts]
                return JsonResponse({'response': 'Your appointments:\n' + '\n'.join(lines)})
            return JsonResponse({'response': 'I could not find your user account. Please log in or open chat from your token page.'})

        if intent == 'bed_holds':
            user = token.user if token and getattr(token, 'user', None) else getattr(request, 'user', None)
            if user and user.is_authenticated:
                holds = BedHold.objects.filter(user=user)
                if holds.exists():
                    lines = [f"Hospital: {h.hospital.name} - Held at {h.created_at}" for h in holds]
                    return JsonResponse({'response': 'Your bed holds:\n' + '\n'.join(lines)})
                return JsonResponse({'response': 'You have no active bed holds.'})
            elif token:
                holds = BedHold.objects.filter(hospital=token.hospital)
                if holds.exists():
                    return JsonResponse({'response': f'There are currently {holds.count()} holds at {token.hospital.name}.'})
                return JsonResponse({'response': 'There are no bed holds at this hospital right now.'})

    # Try to resolve the Queue token (if provided)
    token = None
    try:
        if token_id:
            token = Queue.objects.filter(id=token_id).first()
        # if no token but hospital_id provided, we'll handle hospital context below
    except Exception:
        token = None

    # If no hospital context provided but the message mentions a doctor name,
    # try to resolve the doctor globally and answer doctor-specific queue size.
    if not hospital_id:
        try:
            for d in Doctor.objects.all():
                dname = (d.name or '').lower()
                if not dname:
                    continue
                if dname in text:
                    total = Queue.objects.filter(doctor=d).count()
                    return JsonResponse({'response': f'There are {total} people in Dr. {d.name}\'s queue at {d.hospital.name}.'})
                parts = dname.split()
                if parts and parts[-1] in text:
                    total = Queue.objects.filter(doctor=d).count()
                    return JsonResponse({'response': f'There are {total} people in Dr. {d.name}\'s queue at {d.hospital.name}.'})
        except Exception:
            pass

    # Simple rule-based handlers to answer from the system/database
    # If chat provided hospital context but no token, return hospital summary when the user asks general questions
    if hospital_id and not token:
        try:
            hosp = Hospital.objects.filter(id=int(hospital_id)).first()
        except Exception:
            hosp = None
        if hosp:
            # If user asked about a specific doctor, try to match by name within this hospital
            try:
                matched_doctor = None
                for d in Doctor.objects.filter(hospital=hosp):
                    dname = (d.name or '').lower()
                    if dname and dname in text:
                        matched_doctor = d
                        break
                    # try last name match
                    parts = dname.split()
                    if parts and parts[-1] in text:
                        matched_doctor = d
                        break
                if matched_doctor and ('queue' in text or 'people' in text or 'in queue' in text or 'ahead' in text):
                    total = Queue.objects.filter(doctor=matched_doctor).count()
                    return JsonResponse({'response': f'There are {total} people in Dr. {matched_doctor.name}\'s queue at {hosp.name}.'})
            except Exception:
                # if doctor lookup fails, fall back to hospital summary
                matched_doctor = None

            # gather basic stats
            doctors = Doctor.objects.filter(hospital=hosp).count()
            queue_count = Queue.objects.filter(hospital=hosp).count()
            beds_avail = Bed.objects.filter(hospital=hosp).aggregate(total_available=Sum('available'))['total_available'] or 0
            beds_occ = Bed.objects.filter(hospital=hosp).aggregate(total_occupied=Sum('occupied'))['total_occupied'] or 0
            summary = f"{hosp.name}: {doctors} doctors available. Current queue size: {queue_count}. Beds available: {beds_avail}, occupied: {beds_occ}."
            return JsonResponse({'response': summary})
    
    try:
        # Handle direct 'who is my doctor' queries
        if any(phrase in text for phrase in ("who is my doctor", "who's my doctor", 'my doctor', 'who is my primary', 'who is my pcp')):
            # Prefer token.doctor, then upcoming appointment, then fallback
            if token and getattr(token, 'doctor', None):
                d = token.doctor
                return JsonResponse({'response': f'Your doctor is {d.name} ({d.specialty}).'})
            user = token.user if token and getattr(token, 'user', None) else getattr(request, 'user', None)
            if user and getattr(user, 'is_authenticated', False):
                appt = Appointment.objects.filter(user=user).order_by('date', 'time').first()
                if appt:
                    d = appt.doctor
                    return JsonResponse({'response': f'Your next appointment is with {d.name} ({d.specialty}) on {appt.date} at {appt.time}.'})
                return JsonResponse({'response': 'I could not find a doctor on your upcoming appointments. If you think this is an error, please check your bookings page.'})
            return JsonResponse({'response': 'I could not determine your doctor. Open chat from your token page or log in so I can look up your records.'})

        # How many people in queue / people ahead / people with me
        if ('how many' in text and 'queue' in text) or 'people ahead' in text or 'ahead of me' in text or 'in queue with me' in text or ('how many' in text and 'people' in text and 'queue' in text):
            if token:
                if token.doctor_id:
                    total = Queue.objects.filter(doctor=token.doctor).count()
                    ahead = Queue.objects.filter(doctor=token.doctor, position__lt=token.position).count()
                    behind = total - ahead - 1
                    return JsonResponse({'response': f'There are {total} people in Dr. {token.doctor.name}\'s queue. You are position {token.position}; {ahead} people are ahead of you and {behind} are behind you.'})
                else:
                    total = Queue.objects.filter(hospital=token.hospital).count()
                    ahead = Queue.objects.filter(hospital=token.hospital, position__lt=token.position).count()
                    behind = total - ahead - 1
                    return JsonResponse({'response': f'There are {total} people in the hospital queue. You are position {token.position}; {ahead} people are ahead of you and {behind} are behind you.'})
            return JsonResponse({'response': 'I could not find your token. Open chat from your token page so I can check the queue for you.'})

        if 'wait' in text or 'waiting' in text:
            if token:
                position = token.position
                avg_time = 10
                mins = position * avg_time
                return JsonResponse({'response': f'Your estimated waiting time is {mins} minutes (position {position}).'})
            return JsonResponse({'response': 'I can tell your waiting time if you open chat from your token page.'})

        if 'position' in text or 'where am i' in text or 'queue position' in text:
            if token:
                return JsonResponse({'response': f'Your current queue position is {token.position}.'})
            return JsonResponse({'response': 'I could not find your token. Open chat from your token page to get position.'})

        if 'token' in text or 'token number' in text:
            if token:
                return JsonResponse({'response': f'Your token number is {token.token_number} and your position is {token.position}.'})
            return JsonResponse({'response': 'No token found for this chat session.'})

        if 'appointment' in text or 'bookings' in text or 'my bookings' in text:
            # Prefer token.user, else authenticated user
            user = token.user if token and getattr(token, 'user', None) else getattr(request, 'user', None)
            if user and user.is_authenticated:
                appts = Appointment.objects.filter(user=user).order_by('date', 'time')
                if not appts.exists():
                    return JsonResponse({'response': 'You have no upcoming appointments.'})
                lines = [f"{a.doctor.name} on {a.date} at {a.time}" for a in appts]
                return JsonResponse({'response': 'Your appointments:\n' + '\n'.join(lines)})
            return JsonResponse({'response': 'I could not find your user account. Please log in or open chat from your token page.'})

        if 'bed' in text or 'hold' in text:
            # show bed holds for the user or hospital
            user = token.user if token and getattr(token, 'user', None) else getattr(request, 'user', None)
            if user and user.is_authenticated:
                holds = BedHold.objects.filter(user=user)
                if holds.exists():
                    lines = [f"Hospital: {h.hospital.name} - Held at {h.created_at}" for h in holds]
                    return JsonResponse({'response': 'Your bed holds:\n' + '\n'.join(lines)})
                return JsonResponse({'response': 'You have no active bed holds.'})
            elif token:
                # show holds for the token's hospital
                holds = BedHold.objects.filter(hospital=token.hospital)
                if holds.exists():
                    return JsonResponse({'response': f'There are currently {holds.count()} holds at {token.hospital.name}.'})
                return JsonResponse({'response': 'There are no bed holds at this hospital right now.'})

    except Exception as e:
        logger.exception('Error in system intent handler')

    # Fallback: forward to Gemini for general chit-chat
    try:
        model = genai.GenerativeModel('gemini-2.5-flash')
        logger.debug(f"Sending message to Gemini API: {message}")
        response = model.generate_content(message)
        import pprint
        logger.debug(f"Raw Gemini API response:\n{pprint.pformat(getattr(response, '__dict__', response))}")
        reply = getattr(response, 'text', None) or (response.get('output') if isinstance(response, dict) else None)
        if not reply:
            reply = 'Sorry, the model returned an empty response.'
    except Exception as e:
        logger.error(f"Error generating response with Gemini: {str(e)}")
        reply = f'Error: {str(e)}'
>>>>>>> b73893c741ba2eacf891890fb9034369e7c8cf1c

    return JsonResponse({'response': reply})
