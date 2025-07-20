from django.http import JsonResponse
from .or_tools import TimeTableScheduler
import traceback
from .models import Department, Program,Hall,Lecture,Level,Group,Subject,Teacher,Today,Period,TeacherTime,Distribution,Table
import uuid
from datetime import datetime
import os
from django.core.files import File
from django.conf import settings
from io import BytesIO
from django.core.files.base import ContentFile
from rest_framework.decorators import api_view

@api_view(['POST'])
def run_scheduler_view(request):
    try:
        semester=request.data['semester']
        print(f"Received semester: {semester}")
        scheduler = TimeTableScheduler(semester_filter=semester)
        timestamp = datetime.now().strftime("%Y-%m-%d_%I-%M-%p")  # %I: ساعة بنظام 12 ساعة، %p: AM/PM
        unique_id = str(uuid.uuid4())[:8]
        filename = f"schedule_{timestamp}_{unique_id}.xlsx"
        scheduler.run()

         
        django_file = File(scheduler.temp_file)
        if django_file.size>0:
            table_instance = Table.objects.create(name=f"جدول {timestamp}")
            table_instance.table.save(filename,django_file, save=True)
        else:
            return JsonResponse({'status': 'error', 'message': 'الملف الناتج فارغ، يرجى التحقق من البيانات المدخلة.'}, status=400)
        
        for row in scheduler.generated_schedule:
            fk_hall = Hall.objects.get(pk=row['room_id'])
            fk_day = Today.objects.get(pk=row['day_id'])
            fk_period = Period.objects.get(pk=row['time_id'])
            fk_distribution = Distribution.objects.get(pk=row['course_id'])
            row_data = Lecture(
                fk_hall=fk_hall,
                fk_day=fk_day,
                fk_period=fk_period,
                fk_distribution=fk_distribution,
                fk_table=table_instance
            )
            row_data.save()            
        return JsonResponse({'status': 'success', 'message': 'تم تنفيذ الجدولة بنجاح. تحقق من الملفات المخرجة.'})
    except Exception as e:
        error_message = traceback.format_exc()
        return JsonResponse({'status': 'error', 'message': str(e), 'trace': error_message}, status=500)