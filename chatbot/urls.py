from django.urls import path
from . import views

app_name = 'chatbot'

urlpatterns = [
    path('<int:token_id>/', views.chatbot_view, name='chatbot'),
    path('<int:token_id>/chat/', views.chat_message, name='chat_message'),
    path('<int:token_id>/waiting_time/', views.waiting_time, name='waiting_time'),
    path('<int:token_id>/queue_status/', views.queue_status, name='queue_status'),
]
