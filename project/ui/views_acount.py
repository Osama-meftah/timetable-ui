import requests
from django.contrib import messages
from .utils import *
from django.shortcuts import render, redirect
from .utils import api_post,Endpoints,api_get_with_token
from rest_framework.decorators import api_view
from rest_framework.response import Response


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
        succes,data=handle_response(request,response)

        if succes and data is not None:
            tokens = data.get("tokens")
            request.session['token'] = tokens['access']
            request.session['refresh_token'] = tokens['refresh']
            return redirect('dashboard')  # Redirect to a home page or dashboard
        
        return render(request,'login.html')

@api_view(['GET'])
def send_reseat_mail(request):
    token = request.session.get('token')
    if not token:
        return Response({"error": "Token not found in session"})

    # استدعاء دالة خارجية مع التوكن
    response= api_get_with_token(Endpoints.send_reseat_email, token=token)
    handle_response(request,response)
    return redirect('login') # من اجل الرجوع لنفس الصفحة لن يرجع الى login بسبب midleware

@api_view(['POST','GET'])       
def reseat_teacheer_password(request, uidb64, token):
    if request.method=='POST':
        password=request.data["password"]
        confirm_password=request.data["confirm_password"]
        if password!=confirm_password:
            messages.error(request,"كلمات المرور غير متطابقه")
            return redirect(request.path)
        else:
            data=    {"uidb64":uidb64,"token":token,"password":password}
            response=api_post(Endpoints.reseat_teacheer_password,data=data)
            handle_response(request,response)
            return redirect('logout')
    return render(request, "reset_password.html")
     
def logout_view(request):
        request.session.flush()  # Clear the session
        messages.success(request, "Logged out successfully!")
        return redirect('login')  # Redirect to the login page