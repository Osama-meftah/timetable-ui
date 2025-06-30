from django.urls import path,include
from .views import *
from rest_framework.routers import DefaultRouter


router = DefaultRouter()
router.register('departments',DepartmentViewSet )  
router.register('halls',HallViewSet )  
router.register('programs',ProgramViewSet )  
router.register('levels',LevelViewSet )  
router.register('subjects',SubjectViewSet )  
router.register('teachers',TeacherViewSet )  
router.register('groups',GroupViewSet )  
router.register('todays',TodayViewSet )  # تسجيل ViewSet
router.register('periods',PeriodViewSet )  # تسجيل ViewSet
router.register('teacherTimes',TeacherTimeViewSet )  
router.register('distributions',DistributionViewSet )  
router.register('lectures',LectureViewSet )  
router.register('tables',TableViewSet )  

urlpatterns =[
    path('',include(router.urls)),
]
 
