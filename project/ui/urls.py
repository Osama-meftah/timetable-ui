from django.urls import path
from . import views

urlpatterns = [
    path('', views.login, name='login'),
    path('dashboard/', views.dashboard, name='dashboard'),
    
    
    path('teachers/', views.TeacherManagementView.as_view(), name='teachers_management'),
    path('teachers/add/', views.TeacherManagementView.as_view(), name='add_teacher'),
    path('teachers/edit/<int:id>/', views.TeacherManagementView.as_view(), name='edit_teacher'),
    path('teachers/delete/<int:id>/', views.TeacherDeleteView.as_view(), name='delete_teacher'),  
 
      
    path('teacherswithcourses/add/', views.TeacherAvailabilityAndCoursesView.as_view(), name='add_edit_teacher_with_courses'),
    path('teacherswithcourses/edit/<int:id>/', views.TeacherAvailabilityAndCoursesView.as_view(), name='add_edit_teacher_with_courses'),
    # path('teacherswithcourses/delete/<int:pk>/', views.delete_teacher_with_courses_view, name='delete_teacher_with_courses'),  
      

    path('courses/', views.CoursesView.as_view(), name='courses_management'),
    path('courses/add/', views.CoursesView.as_view(), name='add_course'),
    path('courses/edit/<int:id>/', views.CoursesView.as_view(), name='edit_course'),
    path('courses/delete/<int:id>/', views.CoursesView.as_view(), name='delete_course'),
    
    
    path('rooms/', views.RoomsView.as_view(), name='rooms_management'),
    path('rooms/add/', views.RoomsView.as_view(), name='add_room'),
    path('rooms/edit/<int:id>/', views.RoomsView.as_view(), name='edit_room'),
    path('rooms/delete/<int:id>/', views.RoomsView.as_view(), name='delete_room'),
    
    
    path('departments/', views.DepartmentsManagementView.as_view(), name='departments_management'),
    path('departments/add/', views.DepartmentsManagementView.as_view(), name='add_department'),
    path('departments/edit/<int:id>/', views.DepartmentsManagementView.as_view(), name='edit_department'),
    path('departments/delete/<int:id>/', views.DepartmentsManagementView.as_view(), name='delete_department'),
    
    
    path('program/add/', views.AddAndEditProgramView.as_view(), name='add_program'),
    path('program/edit/<int:id>/', views.AddAndEditProgramView.as_view(), name='edit_program'),
    
    
    path('timetable/', views.TimeTableSettingsView.as_view(), name='schedule_creation'),
]