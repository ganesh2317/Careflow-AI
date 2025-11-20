from django.urls import path
from . import views

app_name = 'appointments'

urlpatterns = [
    path('book/<int:hospital_id>/', views.book_appointment, name='book_appointment'),
]
