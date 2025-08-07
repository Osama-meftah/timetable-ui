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
        return render(request,'add_admin.html')   