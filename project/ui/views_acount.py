import requests
from django.contrib import messages
from .utils import *
from django.shortcuts import render, redirect
from .utils import api_post,Endpoints,api_get_with_token
from rest_framework.decorators import api_view
from rest_framework.response import Response

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
        response = api_post(Endpoints.login, data,request)
        succes,data=handle_response(request,response)

        if succes and data is not None:
            tokens = data.get("tokens")
            token=tokens['access']
            user=api_get_with_token(Endpoints.user,token=token)
            request.session['user']=user
            request.session['token'] = token
            request.session['refresh_token'] = tokens['refresh']
            return redirect('dashboard')  # Redirect to a home page or dashboard
        else:
            return render(request,'login.html',{"username":username})
        

# @api_view(['GET'])
# def send_reseat_mail(request):
#     token = request.session.get('token')
#     print(token)
#     if not token:
#         return Response({"error": "Token not found in session"})
#     # استدعاء دالة خارجية مع التوكن
#     response= api_get_with_token(Endpoints.send_reseat_email, token=token)
#     handle_response(request,response)
#     return redirect('login') 
@api_view(['GET'])
def send_reseat_mail(request):
    token = request.session.get('token')
    if not token:
        return Response({"error": "Token not found in session"})

    response = api_get_with_token(Endpoints.send_reseat_email, token=token)
    status, data = handle_response(request, response)
    print("Status:", status)
    if status == "success":
        return redirect('login')
    elif status in ["unexpected", "invalid", "none"]:
        print("Unexpected or invalid response:", data)
        # عرض صفحة الخطأ المخصصة
        return render(request, "error.html", {
            "message": "حدث خطأ غير متوقع أثناء الاتصال بالخادم"
        })

    return redirect('login')  # في حال "error" مع رسالة واضحة

@api_view(['GET'])
def send_reseat_mail(request):
    token = request.session.get('token')
    print(token)
    
    if not token:
        return Response({"error": "Token not found in session"})

    # استدعاء دالة خارجية مع التوكن
    response = api_get_with_token(Endpoints.send_reseat_email, token=token)
    
    # استقبال النتيجة من handle_response
    success, _ = handle_response(request, response)

    if success:
        return redirect('login')  # إذا تم بنجاح
    else:
        return redirect(request.path)  # إذا فشل، يرجع لنفس الصفحة أو غيّرها كما تريد

@api_view(['POST','GET'])
def send_forget_password_mail(request):
    if request.method=="POST":
        email=request.POST.get("email")
        data={
        "email":email
        }
        response= api_post(Endpoints.send_forget_password_email,data=data)
        success,_= handle_response(request,response)
         # من اجل الرجوع لنفس الصفحة لن يرجع الى login بسبب midlewar
        if success:
           return redirect('login')
        return redirect(request.path)

    return render(request,'teachers_management/forget_password.html')

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
    return render(request, "teachers_management/reset_password.html")
     
def logout_view(request):
        request.session.flush()  # Clear the session
        messages.success(request, "Logged out successfully!")
        return redirect('login')  # Redirect to the login page