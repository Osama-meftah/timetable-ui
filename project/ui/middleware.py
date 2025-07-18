from django.shortcuts import redirect, render
from rest_framework_simplejwt.tokens import AccessToken
from django.contrib.auth.models import User
from .utils import api_post
class IsLoginMiddleware:
    def __init__(self,get_response):
        self.get_response= get_response
    def __call__(self,request):
        response = self.get_response(request)
        is_logged_in = request.session.get('token') is not None
    
        path=request.path
        token=request.session.get('token')
        accessToken=AccessToken(token)
        is_staff=accessToken['is_staff']
        is_superuser=accessToken['is_superuser']
        if path in  ['/login/', '/']:
            if is_logged_in and path == '/login/' or path == '/':

                # user=userToken
                print(f"is_staff {is_staff} - is_is_superuser  {is_superuser}")
                if is_staff or is_superuser:
                    return redirect('dashboard')
                else:
                    return redirect('teachers_management')
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
        