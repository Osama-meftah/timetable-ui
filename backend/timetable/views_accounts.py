from .models import *
from django.contrib.auth.models import User 
from rest_framework.decorators import api_view,permission_classes
from django.http import JsonResponse
from django.contrib import messages
from django.shortcuts import redirect,render
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import MyTokenObtainPairSerializer,UserSerializer
import requests

from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.core.mail import send_mail
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.conf import settings
from rest_framework import status
from rest_framework import generics
from rest_framework.views import APIView
from django.contrib.auth.models import User, Permission
from .serializers import UserCreateSerializer, PermissionSerializer

@api_view(['POST'])
def Login(request):
    if request.method == 'POST':
        username = request.data.get('username')
        password = request.data.get('password')
        data= {
            "username": username,
            "password": password
        }        
        response=requests.post("http://127.0.0.1:8001/api/token/", json=data)
        if response.status_code == 200:
            tokens = response.json()
            return Response({"status":"success", "message": "تم تسجيل الدخول بنجاح", "data": {"tokens":tokens}}, status=200)
        else:
            return Response({ "status":"error" ,"message": "خطأ في البريد او كلمة المرور"}, status=status.HTTP_401_UNAUTHORIZED)

@api_view(['POST'])       
def reset_passowrd(request):
    try:
        data=request.data
        uidb64=data['uidb64']
        token=data['token']
        uid: str=urlsafe_base64_decode( uidb64).decode()
        user=User.objects.get(id=uid)
       
    except:
        user=None
    if user and default_token_generator.check_token(user, token):
        if request.method == "POST":
            password = data["password"]
            user.set_password(password)
            user.save()
            return Response({"status":"success","message":"تم تغيير كلمة المرور بنجاح"},status=status.HTTP_200_OK)
    else:
        return Response({"status":"error","message":"الرابط منتهي"},status=status.HTTP_404_NOT_FOUND)
    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def send_reset_email(request):
    try:
        user=request.user
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        from_email = settings.DEFAULT_FROM_EMAIL
        relative_link = f"/reset-password/{uid}/{token}/"
        reset_url = f"{settings.FRONT_END_HOST}{relative_link}"
        subject = "إعادة تعيين كلمة المرور"
        message = f"انقر على الرابط التالي لتعيين كلمة مرور جديدة:\n{reset_url}"
        send_mail(subject, message, from_email, [user.email])
        return Response({"status":"success","message":"تم ارسال رابط تغيير كلمة المرور الى بريدك الالكتروني"})
    except Exception as e:
        return Response({"status":"error","message":f"{e}"})
    
@api_view(['POST'])
def send_forget_password_email(request):
    try:
        data=request.data
        email=data.get("email")
        user=User.objects.filter(email=email).first()
        if user:
            uid=urlsafe_base64_encode(force_bytes(user.pk))
            token=default_token_generator.make_token(user)
            relative_link = f"/reset-password/{uid}/{token}/"
            reset_url = f"{settings.FRONT_END_HOST}{relative_link}"
            from_email = settings.DEFAULT_FROM_EMAIL
            subject = "إعادة تعيين كلمة المرور"
            message = f"انقر على الرابط التالي لتعيين كلمة مرور جديدة:\n{reset_url}"
            send_mail(subject, message, from_email, [user.email])
            return Response({"status":"success","message":"تم ارسال رابط تغيير كلمة المرور الى بريدك الالكتروني"})
        return Response({"status":"error","message":"لا يوجد مستخدم بهذا البريد"})
    except Exception as e:
        return Response({"status":"error","message":f"{e}"})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getuseer(requset):
    try:
        user=UserSerializer(requset.user)
        if user:
            return Response(user.data)
    except Exception as e:
        return Response(f"error {e}")


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

class UserListAPIView(generics.ListAPIView):
    queryset = User.objects.all().order_by('username')
    serializer_class = UserSerializer
    
class UserCreateAPIView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserCreateSerializer


from rest_framework import generics
from rest_framework.permissions import IsAdminUser # استيراد هام لحماية الواجهة
from .serializers import UserRoleSerializer # استيراد الـ Serializer الجديد
from django.contrib.auth.models import User

# ... (باقي الـ Views لديك)

class UserDetailAPIView(generics.RetrieveUpdateAPIView):
    """
    واجهة API لجلب (GET) وتحديث (PATCH) بيانات مستخدم معين.
    """
    queryset = User.objects.all()
    serializer_class = UserRoleSerializer
    permission_classes = [IsAdminUser] 