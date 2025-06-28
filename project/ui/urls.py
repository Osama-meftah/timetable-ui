from django.urls import path
from . import views

urlpatterns = [
    path('', views.login, name='login'),
    path('dashboard/', views.dashboard, name='dashboard'),
    
    
    path('teachers/', views.TeachersView.as_view(), name='teachers_management'),
    path('teachers/add/', views.TeacherFormView.as_view(), name='add_teacher'),
    path('teachers/edit/<int:id>/', views.TeacherFormView.as_view(), name='edit_teacher'),
    path('teachers/delete/<int:id>/', views.TeacherDeleteView.as_view(), name='delete_teacher'),  
      
      
      
    path('teacherswithcourses/add/', views.TeacherAvailabilityAndCoursesView.as_view(), name='add_edit_teacher_with_courses'),
    path('teacherswithcourses/edit/<int:id>/', views.TeacherAvailabilityAndCoursesView.as_view(), name='add_edit_teacher_with_courses'),
    path('teacherswithcourses/delete/<int:pk>/', views.delete_teacher_with_courses_view, name='delete_teacher_with_courses'),  
      
    
    
    
    path('courses/', views.CoursesView.as_view(), name='courses_management'),
    path('courses/add/', views.CoursesView.as_view(), name='add_course'),
    path('courses/edit/<int:id>/', views.CoursesView.as_view(), name='edit_course'),
    path('courses/delete/<int:id>/', views.CoursesView.as_view(), name='delete_course'),
    
    
    
    path('rooms/', views.rooms_management_view, name='rooms_management'),
    path('rooms/add/', views.add_edit_room_view, name='add_room'),
    path('rooms/edit/<int:pk>/', views.add_edit_room_view, name='edit_room'),
    path('rooms/delete/<int:pk>/confirm/', views.confirm_delete_room_view, name='confirm_delete_room'),
    
    
    path('departments/', views.departments_management_view, name='departments_management'),
    path('departments/add/', views.add_edit_department_view, name='add_department'),
    path('departments/edit/<int:pk>/', views.add_edit_department_view, name='edit_department'),
    path('departments/delete/<int:pk>/', views.delete_department_view, name='delete_department'),
    
    
    
    path('timetable/', views.timetable_settings_view, name='schedule_creation'),
   
]