from .models import *
from django.contrib.auth.models import User 
from rest_framework.decorators import api_view
from django.http import JsonResponse
from django.core.mail import send_mail
from django.contrib import messages
from django.shortcuts import redirect
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import MyTokenObtainPairSerializer
import requests

@api_view(['POST'])
def Login(request):
    if request.method == 'POST':
        username = request.data.get('username')
        password = request.data.get('password')
        data= {
            "username": username,
            "password": password
        }
        print(data)
        
        response=requests.post("http://127.0.0.1:8001/api/token/", json=data)

        if response.status_code == 200:
            tokens = response.json()
            return JsonResponse({'message': 'Login successful', 'tokens': tokens}, status=200)
        else:
            return JsonResponse({'error': 'Invalid credentials'}, status=400)

class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

