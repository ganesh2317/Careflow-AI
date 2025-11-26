from django.urls import path
from . import views

app_name = 'chatbot'

urlpatterns = [
    path('<int:token_id>/', views.chatbot_view, name='chatbot'),
    path('<int:token_id>/waiting_time/', views.waiting_time, name='waiting_time'),
    path('<int:token_id>/queue_status/', views.queue_status, name='queue_status'),
    path('message/<int:token_id>/', views.chat_message, name='chat_message'),  # token-specific chat_message POST endpoint
    path('general/', views.general_chat_view, name='general_chat'),
    path('general/chat/', views.chat_message, name='general_chat_message'),
]
