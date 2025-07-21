import requests
from django.contrib import messages
from .utils import *
from django.shortcuts import render, redirect
from .utils import api_post,Endpoints

# from rest_framework_simplejwt.views import TokenObtainPairView
# from .serializers import MyTokenObtainPairSerializer

# class MyTokenObtainPairView(TokenObtainPairView):
#     serializer_class = MyTokenObtainPairSerializer
    
def LoginView(request):
    if request.method == "GET":
        return render(request, 'login.html')
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        data = {
            "username": username,
            "password": password
        }
        response = api_post(Endpoints.login, data)
        tokens = response.get("tokens")
        # print(tokens)

        if tokens:
            # refresh_token = tokens.get("refresh")
            # token=api_post("token/refresh/",{"refresh":refresh_token})
            # print(token)
            request.session['token'] = tokens['access']
            request.session['refresh_token'] = tokens['refresh']
            messages.success(request, "Login successful!")
            return redirect('dashboard')  # Redirect to a home page or dashboard
        else:
            messages.error(request, "Invalid credentials. Please try again.")

def logout_view(request):
        request.session.flush()  # Clear the session
        messages.success(request, "Logged out successfully!")
        return redirect('login')  # Redirect to the login page