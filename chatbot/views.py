import os
import google.generativeai as genai
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from queues.models import Queue

# Configure Gemini API
genai.configure(api_key='AIzaSyATwaNkpl9jECLM6GE1w8U7ncw4bRW_ksw')  # Replace with actual key or set in env

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

@csrf_exempt
@require_POST
def chat_message(request, token_id=None):
    message = request.POST.get('message', '').strip()

    if not message:
        return JsonResponse({'response': 'Please enter a message.'})

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

    return JsonResponse({'response': reply})
