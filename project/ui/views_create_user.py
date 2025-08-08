import requests
from django.contrib import messages
from .utils import *
from django.shortcuts import render, redirect
from .utils import api_post,Endpoints,api_get_with_token
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.views import View


class CreateAdmin(View):
    def get(self, request):
        user=request.session.get('user')
        if not user or user['is_superuser'] == False:
            return redirect("teacher_dashboard")
        print(user['is_superuser'])
        return render(request,'add_admin.html',{'teacher': user})   