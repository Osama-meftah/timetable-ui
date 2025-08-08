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
        if response['results']:
            context = {
                'tables':response['results']
            }
            return render(request, 'timetables/tables_list.html', context)
        return render(request, 'timetables/tables_list.html')

    def post(self, request):
        semester= request.POST.get('semester')
        random_enabled = request.POST.get('random')
        if not semester:
            messages.error(request, "يرجى تحديد الفصل الدراسي")
        response=api_post(Endpoints.tables, data={"semester":semester,"random":random_enabled},request=request)
        conflict = []
        available_unscheduled = []
        if response:
            conflict = response.get('conflicts', [])
            available_unscheduled = response.get('available_unscheduled', [])
            
            # حفظ في الجلسة فقط إذا كانت البيانات غير فارغة
            if conflict:
                request.session['conflicts'] = conflict
            else:
                request.session.pop('conflicts', None)

            if available_unscheduled:
                request.session['available_unscheduled'] = available_unscheduled
            else:
                request.session.pop('available_unscheduled', None)

        else:
            # لا يوجد استجابة، احذف أي بيانات قديمة من الجلسة
            request.session.pop('conflicts', None)
            request.session.pop('available_unscheduled', None)
        return render(request,'timetables/list.html',{"selected_random":random_enabled,"selected_semester":semester,"conflicts":conflict,'available_unscheduled':available_unscheduled})

class TableDeleteView(View):
    def post(self, request, id):
        print(f"Deleting table with ID: {id}")
        return api_delete(f"{Endpoints.tables}{id}/", request=request,redirect_to='table')
        # return redirect('table')
        
class LecturesView(View):
    def get(self, request, id):
        program_id = request.GET.get('program')
        response = api_get(f"{Endpoints.lectures}{id}/?program={program_id}", request=request)
        # days=api_get(Endpoints.todays, request=request)
        hall=api_get(Endpoints.halls, request=request)
        periods=api_get(Endpoints.periods, request=request)
        programs = api_get(Endpoints.programs, request=request)
        if response.get('lecture'):
            context = {
                'schedule': response.get('lecture'),
                'periods': periods['results'],
                'table_id': id,
                'halls': hall['results'],
                'programs': programs['results'],
            }
            return render(request, 'timetables/lecture_list.html', context)
        messages.error(request, "لا توجد محاضرات لهذا الجدول")
        return redirect('table')