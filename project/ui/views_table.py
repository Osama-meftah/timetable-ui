from django.shortcuts import render, redirect
from django.views import View
import requests
from django.contrib import messages
from .utils import *
from django.middleware.csrf import get_token
from collections import Counter
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import AccessToken
from django.core.cache import cache

class TableView(View):
    def get(self, request):
        response= api_get(Endpoints.tables, request=request)
        if response:
            context = {
                'tables': response
            }
            return render(request, 'timetables/tables_list.html', context)
        return render(request, 'timetables/tables_list.html')

    def post(self, request):
        semester= request.POST.get('semester')
        random_enabled = request.POST.get('random')
        if not semester:
            messages.error(request, "يرجى تحديد الفصل الدراسي")
        response=api_post(Endpoints.tables, data={"semester":semester,"random":random_enabled},request=request)
        return render(request,'timetables/list.html',{"selected_random":random_enabled,"selected_semester":semester})

class TableDeleteView(View):
    def post(self, request, id):
        print(f"Deleting table with ID: {id}")
        return api_delete(f"{Endpoints.tables}{id}/", request=request,redirect_to='table')
        # return redirect('table')
        
class LecturesView(View):
    def get(self, request, id):
        response = api_get(f"{Endpoints.lectures}{id}/", request=request)
        # days=api_get(Endpoints.todays, request=request)
        hall=api_get(Endpoints.halls, request=request)
        periods=api_get(Endpoints.periods, request=request)
        if response.get('lecture'):
            context = {
                'schedule': response.get('lecture'),
                'periods': periods,
                # 'days': days,
                'halls': hall,
            
            }
            return render(request, 'timetables/lecture_list.html', context)
        messages.error(request, "لا توجد محاضرات لهذا الجدول")
        return redirect('table')
    