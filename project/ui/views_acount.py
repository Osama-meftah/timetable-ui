import requests
from django.contrib import messages
from .utils import *
from django.middleware.csrf import get_token
from collections import Counter
from django.shortcuts import render, redirect
import json


BASE_API_URL = "http://127.0.0.1:8001/api/"

def LoginView(request):
    if request.method == "GET":
        access_token = request.session.get('token')
        if access_token:
            return redirect('dashboard')
        return render(request, 'login.html')
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        data = {
            "username": username,
            "password": password
        }
        response = requests.post(f"{BASE_API_URL}login/", json=data)
        
        if response.status_code == 200:
            print(response.json())
            tokens = response.json().get("tokens")
            token = tokens.get("access")
            refresh_token = tokens.get("refresh")
            request.session['token'] = token
            request.session['refresh_token'] = refresh_token
            messages.success(request, "Login successful!")
            return redirect('dashboard')  # Redirect to a home page or dashboard
        else:
            messages.error(request, "Invalid credentials. Please try again.")
    