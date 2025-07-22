from .or_tools import TimeTableScheduler
import traceback
from .models import *
import uuid
from datetime import datetime
from django.core.files import File
from rest_framework.decorators import api_view
from rest_framework.viewsets import ModelViewSet
from .serializers import TableSerializer
from rest_framework.response import Response
from rest_framework import status

class TableViewSet(ModelViewSet):
    queryset = Table.objects.all()
    serializer_class = TableSerializer
    def destroy(self, request, *args, **kwargs):
        try:
            instance=self.get_object()
            Lecture.objects.filter(fk_table=instance).delete()
            if instance.table:
                instance.table.delete(save=False)
            instance.delete()
            return Response({
                "status": "success",
                "message": "تم حذف الجدول والمحاضرات والملف بنجاح ✅"
            }, status=status.HTTP_204_NO_CONTENT)
        
        except Exception as e:
            return Response({
                "status": "error",
                "message": f"حدث خطأ أثناء الحذف: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    def create(self, request, *args, **kwargs):
        try:
            semester = request.data.get('semester')
            if not semester:
                return Response({'status': 'error', 'message': 'يرجى تحديد الفصل الدراسي'}, status=status.HTTP_400_BAD_REQUEST)

            # تشغيل الجدولة
            scheduler = TimeTableScheduler(semester_filter=semester)
            scheduler.run()

            # إنشاء اسم الملف
            timestamp = datetime.now().strftime("%Y-%m-%d_%I-%M-%p")
            unique_id = str(uuid.uuid4())[:8]
            filename = f"schedule_{timestamp}_{unique_id}.xlsx"

            django_file = File(scheduler.temp_file)
            if django_file.size == 0:
                return Response({'status': 'error', 'message': 'الملف الناتج فارغ، يرجى التحقق من البيانات المدخلة.'}, status=status.HTTP_400_BAD_REQUEST)

            # إنشاء الجدول
            table_instance = Table.objects.create(name=f"جدول {timestamp}")
            table_instance.table.save(filename, django_file, save=True)

            # حفظ المحاضرات المرتبطة
            for row in scheduler.generated_schedule:
                Lecture.objects.create(
                    fk_hall=Hall.objects.get(pk=row['room_id']),
                    fk_day=Today.objects.get(pk=row['day_id']),
                    fk_period=Period.objects.get(pk=row['time_id']),
                    fk_distribution=Distribution.objects.get(pk=row['course_id']),
                    fk_table=table_instance
                )

            serializer = self.get_serializer(table_instance)
            return Response({
                "status": "success",
                "message": "تم إنشاء الجدول وتنفيذ الجدولة بنجاح ✅",
                "data": serializer.data
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            error_message = traceback.format_exc()
            return Response({'status': 'error', 'message': str(e), 'trace': error_message}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)