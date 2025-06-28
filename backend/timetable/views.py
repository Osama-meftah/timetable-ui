from .models import *
from .serializers import *
from rest_framework.viewsets import ModelViewSet


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
 
class SubjectViewSet(ModelViewSet):
    queryset=Subject.objects.all()
    serializer_class=SubjectSerializer
    