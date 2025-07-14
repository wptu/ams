from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
import time

@csrf_protect
def login_view(request):
    """
    Handle user login via Thammasat API
    """
    if request.user.is_authenticated:
        return redirect('home')  # Redirect to home if already logged in
        
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        if not username or not password:
            messages.error(request, 'Please provide both username and password')
            return render(request, 'accounts/login.html')
            
        # Authenticate using our custom backend
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome, {user.first_name}!')
            
            # Redirect to the page user was trying to access, or home
            next_page = request.GET.get('next', 'home')
            return redirect(next_page)
        else:
            messages.error(request, 'Invalid credentials or unable to connect to Thammasat API')
    
    return render(request, 'accounts/login.html')

def logout_view(request):
    """
    Handle user logout
    """
    logout(request)
    messages.info(request, 'You have been logged out')
    return redirect('login')

@login_required
def profile_view(request):
    """
    Display user profile information
    """
    return render(request, 'accounts/profile.html')

def home_view(request):
    """
    Home page view
    """
    return render(request, 'accounts/home.html')


def test_ping(request):
    """
    Simple test endpoint that returns immediately
    """
    return HttpResponse("pong")


def test_json(request):
    """
    Simple JSON test endpoint
    """
    return JsonResponse({"status": "ok", "message": "API is working"})
