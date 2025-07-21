from .models import *
from .serializers import *
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework import status
from .utils import create_random_password, extract_username_from_email, send_password_email

class DepartmentViewSet(ModelViewSet):
    queryset=Department.objects.all()
    serializer_class= DepartmentSerializer
    
    
class ProgramViewSet(ModelViewSet):
    queryset=Program.objects.all()
    serializer_class=ProgramSerializer
    
class GroupViewSet(ModelViewSet):
    queryset=Group.objects.all()
    serializer_class=GroupSerializer
    
class TeacherTimeViewSet(ModelViewSet):
    queryset=TeacherTime.objects.all()
    serializer_class=TeacherTimeSerializer
    
class DistributionViewSet(ModelViewSet):
    queryset=Distribution.objects.all()
    serializer_class=DistributionSerializer
    
class LectureViewSet(ModelViewSet):
    queryset=Lecture.objects.all()
    serializer_class=LectureSerializer

class HallViewSet(ModelViewSet):
    queryset=Hall.objects.all()
    serializer_class=HallSerializer
   
class TodayViewSet(ModelViewSet):
    queryset=Today.objects.all()
    serializer_class=TodaySerializer
    
class PeriodViewSet(ModelViewSet):
    queryset=Period.objects.all()
    serializer_class=PeriodSerializer
    
class TableViewSet(ModelViewSet):
    queryset=Table.objects.all()
    serializer_class=TableSerializer

class LevelViewSet(ModelViewSet):
    queryset=Level.objects.all()
    serializer_class=LevelSerializer
    
class TeacherViewSet(ModelViewSet):
    queryset=Teacher.objects.all()
    serializer_class=TeacherSerializer
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            password=create_random_password()
            email=serializer.data['teacher_email']
            teacher_name=serializer.data['teacher_name']
            teacher_status=serializer.data['teacher_status']
            is_staff=serializer.data.get('is_staff', False)
            teacher_id=request.data.get('id', None)
        
            if not email:
                return Response({'status': 'error', 'message': 'البريد الإلكتروني واسم المستخدم مطلوبان.'}, status=400)
            
            username= extract_username_from_email(email)
            user = User.objects.create_user(username=username, email=email, is_staff=is_staff)
            if User.objects.filter(email=email).exists():
                return Response({"status": "error","message": "البريد الذي ادخلته موجود مسبقا"}, status=status.HTTP_400_BAD_REQUEST)
            user.set_password(password)
            user.save()

            teacher = Teacher.objects.create(
            id=teacher_id,
            user=user,
            teacher_name=teacher_name,
            teacher_status=teacher_status,
            teacher_email=email
                )
            teacher.save()
            if teacher_status == 'active':
                send_password_email(user, password)
            
            # if Teacher.objects.filter(username=username).exists():
                # return Response({"error": "User with this username already exists."}, status=status.HTTP_400_BAD_REQUEST)
            return Response({
                "status": "success",
                "message": "Teacher created successfully.",
                "data": serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class SubjectViewSet(ModelViewSet):
    queryset=Subject.objects.all()
    serializer_class=SubjectSerializer
    