from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from .utils import *
from .serializers import *


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
        
        
# في view الخاص برفع البرامج
class ProgramUploadView(APIView):
    parser_classes = [MultiPartParser]

    def post(self, request):
        return handle_upload(
            request=request,
            model=Program,
            serializer_class=ProgramSerializer,
            required_fields=["program_name", "department_name"],
            get_existing=lambda data: Program.objects.filter(
                program_name=data["program_name"],
                fk_department__name__iexact=data["department_name"]
            ).first(),
            prepare_data=lambda row: {
                "program_name": row.get("program_name", "").strip(),
                "department_name": row.get("department_name", "").strip()
            },
            success_message_singular="برنامج"
        )



class LevelUploadView(APIView):
    parser_classes = [MultiPartParser]

    def post(self, request):
        return handle_upload(
            request=request,
            model=Level,
            serializer_class=LevelSerializer,
            required_fields=["level_name", "program_name", "number_students"],
            get_existing=lambda data: Level.objects.filter(
                level_name=data["level_name"],
                fk_program__program_name__iexact=data["program_name"]
            ).first(),
            prepare_data=lambda row: {
                "level_name": row.get("level_name", "").strip(),
                "program_name": row.get("program_name", "").strip(),
                "number_students": int(row.get("number_students", 0))
            },
            success_message_singular="مستوى"
        )


# class LevelUploadView(APIView):
#     parser_classes = [MultiPartParser]

#     def post(self, request):
#         return handle_upload(
#             request=request,
#             model=Level,
#             serializer_class=LevelSerializer,
#             required_fields=["level_name", "fk_program_id", "number_students"],
#             get_existing=lambda data: Level.objects.filter(
#                 level_name=data["level_name"], fk_program_id=data["fk_program_id"]
#             ).first(),
#             prepare_data=lambda row: {
#                 "level_name": row.get("level_name", "").strip(),
#                 "fk_program_id": int(row.get("fk_program_id")),
#                 "number_students": int(row.get("number_students"))
#             },
#             success_message_singular="مستوى"
#         )

# class TeacherUploadView(APIView):
#     parser_classes = [MultiPartParser]

#     def post(self, request):
#         return handle_upload(
#             request=request,
#             model=Teacher,
#             serializer_class=TeacherSerializer,
#             required_fields=["teacher_name"],  # فقط الاسم هنا
#             get_existing=lambda data: Teacher.objects.filter(teacher_email=data["teacher_email"]).first(),
#             prepare_data=lambda row: prepare_teacher_data(row),
#             success_message_singular="مدرس"
#         )

from django.contrib.auth.models import User
from .utils import create_random_password, extract_username_from_email, send_password_email

class TeacherUploadView(APIView):
    parser_classes = [MultiPartParser]

    def post(self, request):
        return handle_upload(
            request=request,
            model=Teacher,
            serializer_class=TeacherSerializer,
            required_fields=["teacher_name", "teacher_email"],
            get_existing=lambda data: Teacher.objects.filter(teacher_email=data["teacher_email"]).first(),
            prepare_data=self.__class__.prepare_teacher_data,  # الحل هنا
            success_message_singular="مدرس"
        )

    @staticmethod
    def prepare_teacher_data(row):
        email = str(row.get("teacher_email", "")).strip()
        name = str(row.get("teacher_name", "")).strip()
        phone = str(row.get("teacher_phone", "")).strip()
        address = str(row.get("teacher_address", "")).strip()
        status = str(row.get("teacher_status", "نشط")).strip()
        is_staff = False

        if not email:
            raise ValueError("يجب إدخال البريد الإلكتروني لكل مدرس")

        username = extract_username_from_email(email)

        user = User.objects.filter(username=username).first()
        if not user:
            password = create_random_password()
            user = User.objects.create_user(username=username, email=email, is_staff=is_staff)
            user.set_password(password)
            user.save()
            send_password_email(user, password)
            Teacher.objects.create(
                teacher_name=name,
                teacher_email=email,
                teacher_phone=phone,
                teacher_address=address,
                teacher_status=status,
                user=user
            )
            # أرسل كلمة المرور إن كان المدرس نشطًا
            # if status == "نشط":

        return {
            "teacher_name": name,
            "teacher_email": email,
            "teacher_phone": phone,
            "teacher_address": address,
            "teacher_status": status,
            "user": user.id  # هذا ما سيتم تمريره للـ serializer
        }


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
                "term": {
                    "الأول": "term1",
                    "الثاني": "term2"
                }.get(row.get("term", "").strip(), "")
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
                "hall_status": row.get("hall_status", "").strip(),
            },
            success_message_singular="قاعة"
        )
