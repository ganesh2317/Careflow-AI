import os
import google.generativeai as genai
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from queues.models import Queue

# Configure Gemini API
genai.configure(api_key=os.getenv('GEMINI_API_KEY', 'your-api-key-here'))  # Replace with actual key or set in env

def chatbot_view(request, token_id):
    # Allow anonymous users to access chatbot for their token
    token = get_object_or_404(Queue, id=token_id)
    return render(request, 'chatbot/chat.html', {'token': token, 'token_id': token_id})


def general_chat_view(request):
    return render(request, 'chatbot/general_chat.html')


def waiting_time(request, token_id):
    token = get_object_or_404(Queue, id=token_id)
    position = token.position
    avg_time = 10  # minutes per person (simple heuristic)
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
    message = request.POST.get('message', '')
    if not message:
        return JsonResponse({'response': 'Please enter a message.'})

    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(message)
        reply = response.text if response else 'Sorry, I could not generate a response.'
    except Exception as e:
        reply = f'Error: {str(e)}'

    return JsonResponse({'response': reply})
