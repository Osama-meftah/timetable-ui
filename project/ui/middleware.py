from django.shortcuts import redirect, render
from rest_framework_simplejwt.tokens import AccessToken
from django.contrib.auth.models import User
from .utils import api_post,api_get_with_token,Endpoints
class IsLoginMiddleware:
    def __init__(self,get_response):
        self.get_response= get_response
    def __call__(self,request):
        response = self.get_response(request)
        is_logged_in = request.session.get('token') is not None

        path=request.path
        allow_urls=('/login/','/send_forget_email/','/reset-password/')
       
        if path.startswith(allow_urls):
            if is_logged_in and path == '/login/':
                user=request.session.get("user")
                is_staff=user['is_staff']
                # user=userToken
                if is_staff:
                    return redirect('dashboard')
                else:
                    return redirect('teacher_dashboard')
            return response
        if not is_logged_in:
            return redirect('login')
        return response
        
        
class IsAdminMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        is_logged =request.session.get('token') is not None
        path=request.path

        admin_urls=('/periods/','/timetable/','/program/','/departments/','/rooms/','/teacherswithcourses/','/teachers/','/dashboard/')
        allow_urls=('/login/','/send_forget_email/','/reset-password/')
        if path.startswith(allow_urls):
            return response

        if path.startswith(admin_urls):
            if is_logged:
                user=request.session.get("user")
                is_staff=user['is_staff']
                if is_staff:
                    return response
                return redirect('login')
        return response
        