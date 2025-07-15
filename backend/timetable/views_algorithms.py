from django.http import JsonResponse
from .or_tools import TimeTableScheduler
import traceback
from .models import Department, Program,Hall,Lecture,Level,Group,Subject,Teacher,Today,Period,TeacherTime,Distribution,Table

def run_scheduler_view(request):
    try:
        # program=Program.objects.all()
        # hall=Hall.objects.all()
        # level=Level.objects.all()
        # group=Group.objects.all()
        # subject=Subject.objects.all()
        scheduler = TimeTableScheduler()
        scheduler.run()
        return JsonResponse({'status': 'success', 'message': 'تم تنفيذ الجدولة بنجاح. تحقق من الملفات المخرجة.'})
    except Exception as e:
        error_message = traceback.format_exc()
        return JsonResponse({'status': 'error', 'message': str(e), 'trace': error_message}, status=500)