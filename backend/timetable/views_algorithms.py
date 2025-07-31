from .or_tools import TimeTableScheduler
import traceback
from .models import *
import uuid
from datetime import datetime
from django.core.files import File
from rest_framework.decorators import api_view
from rest_framework.viewsets import ModelViewSet
from .serializers import TableSerializer,LectureSerializer
from rest_framework.response import Response
from rest_framework import status
from .views2 import BaseViewSet
from rest_framework.decorators import action
from collections import defaultdict
from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from .filters import LectureFilter


class TableViewSet(BaseViewSet):
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
            random_enabled = request.data.get('random', 'False')  # Default to 'False' if not provided
            if random_enabled == 'True':
                random_enabled = True
            elif random_enabled == 'False':
                random_enabled = False
            print(f"Random enabled: {random_enabled}")
            if not semester:
                return Response({'status': 'error', 'message': 'يرجى تحديد الفصل الدراسي'}, status=status.HTTP_400_BAD_REQUEST)

            # تشغيل الجدولة
            scheduler = TimeTableScheduler(semester_filter=semester)
            scheduler.random_enabled = random_enabled
            conflict = scheduler.conflicts
            scheduler.run()

            # التحقق من تكرار الجدول بنفس البيانات
            generated_lectures = scheduler.generated_schedule

            existing_tables = Table.objects.filter(semester=semester)

            for table in existing_tables:
                existing_lectures = Lecture.objects.filter(fk_table=table)
                match_count = 0

                for row in generated_lectures:
                    if existing_lectures.filter(
                        fk_hall_id=row['room_id'],
                        fk_day_id=row['day_id'],
                        fk_period_id=row['time_id'],
                        fk_distribution_id=row['course_id']
                    ).exists():
                        match_count += 1

                if match_count == len(generated_lectures):
                    return Response({
                        'status': 'error',
                        'message': f"تم إنشاء جدول مشابه مسبقًا لنفس الفصل الدراسي ({semester})"
                    }, status=status.HTTP_409_CONFLICT)

            # إنشاء اسم الملف
            timestamp = datetime.now().strftime("%Y-%m-%d_%I-%M-%p")
            unique_id = str(uuid.uuid4())[:8]
            filename = f"schedule_{timestamp}_{unique_id}.xlsx"

            if conflict:
                return Response({
                    'status': 'error',
                    'message': 'تم العثور على تعارضات في الجدول الزمني، يرجى مراجعة البيانات المدخلة.',
                    'conflicts': conflict
                })
            if not scheduler.temp_file:
                return Response({'status': 'error', 'message': 'لم يتم إنشاء ملف الجدول الزمني، يرجى التحقق من البيانات المدخلة.'})
            django_file = File(scheduler.temp_file)
            if django_file.size == 0:
                return Response({'status': 'error', 'message': 'الملف الناتج فارغ، يرجى التحقق من البيانات المدخلة.'}, status=status.HTTP_400_BAD_REQUEST)

            # إنشاء الجدول
            table_instance = Table.objects.create(name=f"جدول {timestamp}", semester=semester)
            table_instance.table.save(filename, django_file, save=True)

            # حفظ المحاضرات
            for row in generated_lectures:
                Lecture.objects.create(
                    fk_hall_id=row['room_id'],
                    fk_day_id=row['day_id'],
                    fk_period_id=row['time_id'],
                    fk_distribution_id=row['course_id'],
                    fk_table=table_instance
                )

            serializer = self.get_serializer(table_instance)
            return Response({
                "status": "success",
                "message": "تم إنشاء الجدول وتنفيذ الجدولة بنجاح ✅",
                self.queryset.model.__name__.lower(): serializer.data,
                "log": scheduler.log,
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            error_message = traceback.format_exc()
            return Response({'status': 'error', 'message': str(e), 'trace': error_message}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

def deep_convert(obj):
    if isinstance(obj, defaultdict):
        obj = dict(obj)
    if isinstance(obj, dict):
        return {str(k): deep_convert(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [deep_convert(item) for item in obj]
    else:
        return obj
class LecturesViewSet(BaseViewSet):
    queryset = Lecture.objects.all()
    serializer_class = LectureSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = LectureFilter
    @action(detail=False, methods=['get'], url_path='by-table/(?P<table_id>[^/.]+)')
    def by_table(self, request, table_id=None):
        base_qs = self.queryset.filter(fk_table__id=table_id)
        filtered_qs = LectureFilter(request.GET, queryset=base_qs).qs
        # days=Today.objects.all()
        # periods=Period.objects.all()
        schedule = {}
      
        if not filtered_qs.exists():
        
            return Response({"detail": "لا توجد محاضرات لهذا الجدول"}, status=status.HTTP_404_NOT_FOUND)
        try:
            schedule = defaultdict(lambda: defaultdict(list))
            # serializer = self.get_serializer(lectures, many=True)
            for lec in filtered_qs:
                day = lec.fk_day.get_day_name_display()
                period = f"{lec.fk_period.period_from}-{lec.fk_period.period_to}"     
                schedule[day][period].append({
                    "course": lec.fk_distribution.fk_subject.subject_name,
                    "teacher": lec.fk_distribution.fk_teacher.teacher_name,
                    "hall": lec.fk_hall.hall_name,
                    "program":lec.fk_distribution.fk_group.fk_level.fk_program.program_name,
                    "group": lec.fk_distribution.fk_group.group_name,
                    "level": lec.fk_distribution.fk_group.fk_level.get_level_name_display(),
                })

            return Response({
            "status": "success",
            "message": "تم استرجاع المحاضرات بنجاح ✅",
            self.queryset.model.__name__.lower(): deep_convert(schedule)
            }, status=status.HTTP_200_OK)
        except Exception as e:
            error_message = traceback.format_exc()
            return Response({
                "status": "error",
                "message": str(e),
                "trace": error_message
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
       
    # def get_queryset(self):
    #     table_id = self.kwargs.get('id')
    #     print(table_id)
    #     if table_id:
    #         return self.queryset.filter(fk_table__id=table_id)
    #     return self.queryset
