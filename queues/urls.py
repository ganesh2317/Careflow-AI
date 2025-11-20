from django.urls import path
from . import views

app_name = 'queues'

urlpatterns = [
    path('book/<int:hospital_id>/', views.book_token, name='book_token'),
    path('book/doctor/<int:doctor_id>/', views.book_token_doctor, name='book_token_doctor'),
    path('confirm/<int:token_id>/', views.token_confirm, name='token_confirm'),
    path('query/<int:token_id>/', views.query_token, name='query_token'),
    path('manage/<int:hospital_id>/', views.manage_queue, name='manage_queue'),
    path('increment/<int:hospital_id>/', views.increment_queue, name='increment_queue'),
    path('decrement/<int:hospital_id>/', views.decrement_queue, name='decrement_queue'),
]
