from django.shortcuts import redirect, render
from rest_framework_simplejwt.tokens import AccessToken
from django.contrib.auth.models import User
from .utils import *
class IsLoginMiddleware:
    def __init__(self,get_response):
        self.get_response= get_response
    def __call__(self,request):
        response = self.get_response(request)
        is_logged_in = request.session.get('token') is not None
        # accessToken=AccessToken(token)
        # print(f"access token payload  {accessToken.payload}")

    
        path=request.path
       
        if path in  ['/login/', '/']:
            if is_logged_in and path == '/login/' or path == '/':
                token=request.session.get('token')
                user=api_get_with_token(Endpoints.user,token=token)
                request.session['user']=user
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
        
        
# class IsAdminMiddleware:
#     def __init__(self, get_response):
#         self.get_response = get_response

#     def __call__(self, request):
#         response = self.get_response(request)
#         is_logged =request.session.get('token') is not None
#         path=request.path
#         if path.startswith("/teachers/") and is_logged:
#             return request
#         return redirect("notfound")
        
        # if request.user.is_staff or request.user.is_superuser:
        #     return response
        