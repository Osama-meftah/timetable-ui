from django.urls import path,include
from .views import *
from rest_framework.routers import DefaultRouter


router = DefaultRouter()
router.register('todays',TodayViewSet )  # تسجيل ViewSet
router.register('periods',PeriodViewSet )  # تسجيل ViewSet
router.register('halls',HallViewSet )  
router.register('tables',TableViewSet )  
router.register('programs',ProgramViewSet )  
router.register('levels',LevelViewSet )  
router.register('groups',GroupViewSet )  
router.register('teachers',TeacherViewSet )  
router.register('teacherTimes',TeacherTimeViewSet )  
router.register('subjects',SubjectViewSet )  
router.register('distributions',DistributionViewSet )  
router.register('lectures',LectureViewSet )  

urlpatterns =[
    path('',include(router.urls)),
]
 
