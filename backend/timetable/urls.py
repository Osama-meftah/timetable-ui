from django.urls import path,include
from .views import *
from rest_framework.routers import DefaultRouter
from .views_upload_files import  *
from .views_algorithms import run_scheduler_view


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
    path('teachersUpload/', TeacherUploadView.as_view(), name='teachers-upload'),
    path("uploadDepartments/", DepartmentUploadView.as_view(), name="upload_departments"),
    path('uploadPrograms/', ProgramUploadView.as_view(), name='upload_programs'),
    path('uploadLevels/', LevelUploadView.as_view(), name='upload_levels'),
    path('uploadSubjects/', SubjectUploadView.as_view(), name='upload_subjects'),
    path('uploadHalls/', HallUploadView.as_view(), name='upload_halls'),
    path('run-scheduler/', run_scheduler_view, name='run_scheduler'),


]
 
