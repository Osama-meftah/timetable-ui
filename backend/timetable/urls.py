from django.urls import path,include
from .views import *
from rest_framework.routers import DefaultRouter
from .views_upload_files import  *
from .views_algorithms import run_scheduler_view
from .views_search import *
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views_accounts import Login,MyTokenObtainPairView

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
    path("searchteachers/", SearchTeacherAPIView.as_view(), name="search_teachers_api"),
    path("searchteachersdistribution/", SearchTeacherDistributionAPIView.as_view()),
    path("searchcourses/", SearchCoursesAPIView.as_view()),
    path("searchhalls/", SearchHallsAPIView.as_view(),),
    path('run-scheduler/', run_scheduler_view, name='run_scheduler'),

    # urls acounts
    path('login/', Login, name='create_user'),

    # get token
    path('token/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

]
 
