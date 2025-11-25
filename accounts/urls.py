from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('', views.landing_page, name='landing_page'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),

    path('bookings/', views.user_bookings, name='user_bookings'),
    path('bookings/cancel/<int:appointment_id>/', views.cancel_booking, name='cancel_booking'),
]
