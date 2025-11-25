from django.urls import path
from . import views

app_name = 'beds'

urlpatterns = [
    path('track/<int:hospital_id>/', views.track_beds, name='track_beds'),
    path('hold/<int:hospital_id>/', views.hold_bed, name='hold_bed'),
    path('release_hold/<int:hold_id>/', views.release_bed_hold, name='release_bed_hold'),
]
