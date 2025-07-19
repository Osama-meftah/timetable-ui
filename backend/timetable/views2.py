from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from django.contrib.auth.models import User
from .models import *
from .serializers import *
from .utils import create_random_password, extract_username_from_email, send_password_email

# ViewSet الأساسي الذي يتعامل مع كل العمليات
class BaseViewSet(ModelViewSet):
    success_create_message = "تم الإنشاء بنجاح."
    success_update_message = "تم التحديث بنجاح."
    success_delete_message = "تم الحذف بنجاح."

    error_create_message = "خطأ في بيانات الإدخال."
    error_update_message = "فشل التحديث."

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            instance = serializer.save()
            return Response({
                "status": "success",
                "message": self.success_create_message,
                self.queryset.model.__name__.lower(): serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response({
            "status": "error",
            "message": self.error_create_message,
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "status": "success",
                "message": self.success_update_message,
                self.queryset.model.__name__.lower(): serializer.data
            }, status=status.HTTP_200_OK)
        return Response({
            "status": "error",
            "message": self.error_update_message,
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({
            "status": "success",
            "message": self.success_delete_message
        }, status=status.HTTP_204_NO_CONTENT)


# جميع الكلاسات المتفرعة تستخدم BaseViewSet وتعدل الرسائل فقط

class DepartmentViewSet(BaseViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    success_create_message = "تم إنشاء القسم بنجاح."
    success_update_message = "تم تحديث القسم بنجاح."
    success_delete_message = "تم حذف القسم بنجاح."


class ProgramViewSet(BaseViewSet):
    queryset = Program.objects.all()
    serializer_class = ProgramSerializer
    success_create_message = "تم إنشاء البرنامج بنجاح."
    success_update_message = "تم تحديث البرنامج بنجاح."
    success_delete_message = "تم حذف البرنامج بنجاح."


class GroupViewSet(BaseViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    success_create_message = "تم إنشاء المجموعة بنجاح."
    success_update_message = "تم تحديث المجموعة بنجاح."
    success_delete_message = "تم حذف المجموعة بنجاح."


class TeacherTimeViewSet(BaseViewSet):
    queryset = TeacherTime.objects.all()
    serializer_class = TeacherTimeSerializer
    success_create_message = "تم إنشاء وقت الأستاذ بنجاح."
    success_update_message = "تم تحديث وقت الأستاذ بنجاح."
    success_delete_message = "تم حذف وقت الأستاذ بنجاح."


class DistributionViewSet(BaseViewSet):
    queryset = Distribution.objects.all()
    serializer_class = DistributionSerializer
    success_create_message = "تم إنشاء التوزيع بنجاح."
    success_update_message = "تم تحديث التوزيع بنجاح."
    success_delete_message = "تم حذف التوزيع بنجاح."


class LectureViewSet(BaseViewSet):
    queryset = Lecture.objects.all()
    serializer_class = LectureSerializer
    success_create_message = "تم إنشاء المحاضرة بنجاح."
    success_update_message = "تم تحديث المحاضرة بنجاح."
    success_delete_message = "تم حذف المحاضرة بنجاح."


class HallViewSet(BaseViewSet):
    queryset = Hall.objects.all()
    serializer_class = HallSerializer
    success_create_message = "تم إنشاء القاعة بنجاح."
    success_update_message = "تم تحديث القاعة بنجاح."
    success_delete_message = "تم حذف القاعة بنجاح."


class TodayViewSet(BaseViewSet):
    queryset = Today.objects.all()
    serializer_class = TodaySerializer
    success_create_message = "تم إنشاء اليوم بنجاح."
    success_update_message = "تم تحديث اليوم بنجاح."
    success_delete_message = "تم حذف اليوم بنجاح."


class PeriodViewSet(BaseViewSet):
    queryset = Period.objects.all()
    serializer_class = PeriodSerializer
    success_create_message = "تم إنشاء الفترة بنجاح."
    success_update_message = "تم تحديث الفترة بنجاح."
    success_delete_message = "تم حذف الفترة بنجاح."


class TableViewSet(BaseViewSet):
    queryset = Table.objects.all()
    serializer_class = TableSerializer
    success_create_message = "تم إنشاء الجدول بنجاح."
    success_update_message = "تم تحديث الجدول بنجاح."
    success_delete_message = "تم حذف الجدول بنجاح."


class LevelViewSet(BaseViewSet):
    queryset = Level.objects.all()
    serializer_class = LevelSerializer
    success_create_message = "تم إنشاء المستوى بنجاح."
    success_update_message = "تم تحديث المستوى بنجاح."
    success_delete_message = "تم حذف المستوى بنجاح."


class SubjectViewSet(BaseViewSet):
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer
    success_create_message = "تم إنشاء المادة بنجاح."
    success_update_message = "تم تحديث المادة بنجاح."
    success_delete_message = "تم حذف المادة بنجاح."


class TeacherViewSet(BaseViewSet):
    queryset = Teacher.objects.all()
    serializer_class = TeacherSerializer
    success_create_message = "تم إنشاء المدرس بنجاح."
    success_update_message = "تم تحديث بيانات المدرس بنجاح."
    success_delete_message = "تم حذف المدرس والمستخدم المرتبط بنجاح."

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            password = create_random_password()
            email = serializer.validated_data.get('teacher_email')
            teacher_name = serializer.validated_data.get('teacher_name')
            teacher_status = serializer.validated_data.get('teacher_status')
            is_staff = serializer.validated_data.get('is_staff', False)

            if not email:
                return Response({'status': 'error', 'message': 'البريد الإلكتروني مطلوب.'}, status=status.HTTP_400_BAD_REQUEST)

            username = extract_username_from_email(email)

            if User.objects.filter(username=username).exists():
                return Response({'status': 'error', 'message': f'المستخدم بالاسم {username} موجود مسبقاً.'}, status=status.HTTP_400_BAD_REQUEST)

            user = User.objects.create_user(username=username, email=email, is_staff=is_staff)
            user.set_password(password)
            user.save()

            teacher = Teacher.objects.create(
                user=user,
                teacher_name=teacher_name,
                teacher_status=teacher_status,
                teacher_email=email
            )

            if teacher_status == 'active':
                send_password_email(user, password)

            return Response({
                "status": "success",
                "message": self.success_create_message,
                "teacher": TeacherSerializer(teacher).data
            }, status=status.HTTP_201_CREATED)

        return Response({
            "status": "error",
            "message": "خطأ في بيانات المدرس.",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        user = instance.user
        self.perform_destroy(instance)
        if user:
            user.delete()
        return Response({
            "status": "success",
            "message": self.success_delete_message
        }, status=status.HTTP_204_NO_CONTENT)
# class TeacherViewSet(ModelViewSet):
#     queryset=Teacher.objects.all()
#     serializer_class=TeacherSerializer
#     def create(self, request, *args, **kwargs):
#         serializer = self.get_serializer(data=request.data)
#         if serializer.is_valid():
#             password=create_random_password()
#             email=serializer.data['teacher_email']
#             teacher_name=serializer.data['teacher_name']
#             teacher_status=serializer.data['teacher_status']
#             is_staff=serializer.data.get('is_staff', False)
#             teacher_id=request.data.get('id', None)
        
#             if not email:
#                 return JsonResponse({'status': 'error', 'message': 'البريد الإلكتروني واسم المستخدم مطلوبان.'}, status=400)
#             username= extract_username_from_email(email)
#             user = User.objects.create_user(username=username, email=email, is_staff=is_staff)
#             user.set_password(password)
#             user.save()

#             teacher = Teacher.objects.create(
#             id=teacher_id,
#             user=user,
#             teacher_name=teacher_name,
#             teacher_status=teacher_status,
#             teacher_email=email
#                 )
#             teacher.save()
#             if teacher_status == 'active':
#                 send_password_email(user, password)
            
#             # if Teacher.objects.filter(username=username).exists():
#                 # return Response({"error": "User with this username already exists."}, status=status.HTTP_400_BAD_REQUEST)
#             return Response({
#                 "message": "Teacher created successfully.",
#                 "teacher": serializer.data
#             }, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
