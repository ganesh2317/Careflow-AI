from django.urls import path
from . import views

app_name = 'appointments'

urlpatterns = [
    path('book/<int:hospital_id>/', views.book_appointment, name='book_appointment'),
    path('admin/list/', views.admin_appointment_list, name='admin_appointment_list'),
    path('my/', views.my_bookings, name='my_bookings'),
    path('cancel/<int:appointment_id>/', views.cancel_booking, name='cancel_booking'),
]
