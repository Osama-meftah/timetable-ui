from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from .utils import *


class DepartmentUploadView(APIView):
    parser_classes = [MultiPartParser]

    def post(self, request):
        return handle_upload(
            request=request,
            model=Department,
            serializer_class=DepartmentSerializer,
            required_fields=["name"],
            get_existing=lambda data: Department.objects.filter(name=data["name"]).first(),
            prepare_data=lambda row: {
                "name": row.get("name", ""),
                "description": row.get("description", "")
            },
            success_message_singular="قسم"
        )
class ProgramUploadView(APIView):
    parser_classes = [MultiPartParser]

    def post(self, request):
        return handle_upload(
            request=request,
            model=Program,
            serializer_class=ProgramSerializer,
            required_fields=["program_name", "department_id"],
            get_existing=lambda data: Program.objects.filter(
                program_name=data["program_name"],
                fk_department_id=data["department_id"]  # ✅ التصحيح هنا
            ).first(),
            prepare_data=lambda row: prepare_data_with_fk(
                row=row,
                fk_field="fk_department",
                lookup_field="department_id",
                model=Department,
                display_name="program_name"
            ),
            success_message_singular="برنامج"
        )


class LevelUploadView(APIView):
    parser_classes = [MultiPartParser]

    def post(self, request):
        return handle_upload(
            request=request,
            model=Level,
            serializer_class=LevelSerializer,
            required_fields=["level_name", "fk_program_id", "number_students"],
            get_existing=lambda data: Level.objects.filter(
                level_name=data["level_name"], fk_program_id=data["fk_program_id"]
            ).first(),
            prepare_data=lambda row: {
                "level_name": row.get("level_name", "").strip(),
                "fk_program_id": int(row.get("fk_program_id")),
                "number_students": int(row.get("number_students"))
            },
            success_message_singular="مستوى"
        )


class TeacherUploadView(APIView):
    parser_classes = [MultiPartParser]

    def post(self, request):
        return handle_upload(
            request=request,
            model=Teacher,
            serializer_class=TeacherSerializer,
            required_fields=["teacher_name", "teacher_email"],
            get_existing=lambda data: Teacher.objects.filter(teacher_email=data["teacher_email"]).first(),
            prepare_data=lambda row: {
                "teacher_name": row.get("teacher_name", "").strip(),
                "teacher_email": row.get("teacher_email", "").strip(),
                "teacher_phone": row.get("teacher_phone", "").strip(),
                "teacher_address": row.get("teacher_address", "").strip(),
                "teacher_status": row.get("teacher_status", "نشط").strip()
            },
            success_message_singular="مدرس"
        )
        
class SubjectUploadView(APIView):
    parser_classes = [MultiPartParser]

    def post(self, request):
        return handle_upload(
            request=request,
            model=Subject,
            serializer_class=SubjectSerializer,
            required_fields=["subject_name", "term"],  # حذف fk_level_id
            get_existing=lambda data: Subject.objects.filter(
                subject_name=data["subject_name"],
                term=data["term"]
            ).first(),  # البحث بناءً على الاسم والفصل فقط
            prepare_data=lambda row: {
                "subject_name": row.get("subject_name", "").strip(),
                "term": row.get("term", "").strip(),
            },
            success_message_singular="مادة"
        )

class HallUploadView(APIView):
    parser_classes = [MultiPartParser]

    def post(self, request):
        return handle_upload(
            request=request,
            model=Hall,
            serializer_class=HallSerializer,
            required_fields=["hall_name", "capacity_hall", "hall_status"],
            get_existing=lambda data: Hall.objects.filter(
                hall_name=data["hall_name"]
            ).first(),  # القاعة تعتبر فريدة بالاسم فقط
            prepare_data=lambda row: {
                "hall_name": row.get("hall_name", "").strip(),
                "capacity_hall": int(row.get("capacity_hall", 0)),
                "hall_status": row.get("hall_status", "متاحة").strip(),
            },
            success_message_singular="قاعة"
        )
