from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages

def landing_page(request):
    # If user already logged in, send them to hospitals list directly
    if request.user.is_authenticated:
        return redirect('hospitals:hospital_list')
    return render(request, 'accounts/landing.html')

def login_view(request):
    # If already authenticated, redirect to hospitals
    if request.user.is_authenticated:
        return redirect('hospitals:hospital_list')

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('hospitals:hospital_list')
        else:
            messages.error(request, 'Invalid credentials')
    return render(request, 'accounts/login.html')

def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('hospitals:hospital_list')
    else:
        form = UserCreationForm()
    return render(request, 'accounts/register.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('accounts:landing_page')
