# teachers/views.py
from django.db.models import Q
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import *
from .serializers import *

class SearchTeacherAPIView(APIView):
    def get(self, request):
        query = request.GET.get("q", "").strip()
        try:
            teachers = Teacher.objects.all()
            if query:
                teachers = teachers.filter(teacher_name__icontains=query)

            serializer = TeacherSerializer(teachers, many=True)
            return Response({"results": serializer.data}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                "message": "حدث خطأ أثناء تنفيذ البحث.",
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class SearchTeacherTimeAPIView(APIView):
    def get(self, request):
        query = request.GET.get("q", "").strip().lower()

        teacher_times = TeacherTime.objects.select_related("fk_teacher", "fk_today", "fk_period")

        if query:
            teacher_times = teacher_times.filter(Q(fk_teacher__teacher_name__icontains=query))

        result = {}
        for t in teacher_times:
            teacher = t.fk_teacher
            teacher_id = teacher.id

            if teacher_id not in result:
                serialized_teacher = TeacherSerializer(teacher).data
                result[teacher_id] = {
                    "teacher": serialized_teacher,
                    "availability": []
                }

            result[teacher_id]["availability"].append({
                "day": TodaySerializer(t.fk_today).data,
                "period": PeriodSerializer(t.fk_period).data
            })

        return Response({"results": list(result.values())}, status=status.HTTP_200_OK)




class SearchTeacherDistributionAPIView(APIView):
    def get(self, request):
        query = request.GET.get("q", "").strip().lower()
        teachers = Teacher.objects.all()
        if query:
            teachers = teachers.filter(
                Q(teacher_name__icontains=query) |
                Q(teacher_email__icontains=query)
            )

        distributions = Distribution.objects.select_related(
            "fk_teacher", "fk_subject", "fk_group__fk_level__fk_program"
        ).all()

        teacher_times = TeacherTime.objects.select_related(
            "fk_teacher", "fk_today", "fk_period"
        ).all()

        result = []

        for teacher in teachers:
            teacher_id = teacher.id

            # استخراج المقررات
            courses = []
            for d in distributions:
                if d.fk_teacher.id == teacher_id:
                    courses.append({
                        "subject_name": d.fk_subject.subject_name,
                        "group": d.fk_group.group_name,
                        "level": d.fk_group.fk_level.level_name,
                        "program": d.fk_group.fk_level.fk_program.program_name,
                    })

            # استخراج التوفر الزمني
            availability = []
            print(teacher_times)
            for t in teacher_times:
                if t.fk_teacher.id == teacher_id:
                    availability.append({
                        "day": t.fk_today.get_day_name_display(),
                        "period": f"{t.fk_period.period_from} - {t.fk_period.period_to}"
                    })

            if courses:
                result.append({
                    "teacher": teacher,
                    "courses": courses,
                    "availability": availability
                })

        serializer = TeacherWithDetailsSerializer(result, many=True)
        return Response({"results": serializer.data}, status=status.HTTP_200_OK)


class SearchCoursesAPIView(APIView):
    def get(self, request):
        query = request.GET.get("q", "").strip().lower()
        courses = Subject.objects.all()
        if query:
            courses = courses.filter(subject_name__icontains=query)
        serializer = SubjectSerializer(courses, many=True)
        return Response({"results": serializer.data}, status=status.HTTP_200_OK)


class SearchHallsAPIView(APIView):
    def get(self, request):
        query = request.GET.get("q", "").strip().lower()
        halls = Hall.objects.all()
        if query:
            halls = halls.filter(hall_name__icontains=query)
        serializer = HallSerializer(halls, many=True)
        return Response({"results": serializer.data}, status=status.HTTP_200_OK)
