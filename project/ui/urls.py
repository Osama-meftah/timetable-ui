from django.urls import path
from . import views
from .views_acount import LoginView, logout_view

urlpatterns = [
    path('login/', LoginView, name='login'),
    path('logout/', logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    # path()
    
    
    path('teachers/', views.TeacherManagementView.as_view(), name='teachers_management'),
    path('teachers/add/', views.TeacherManagementView.as_view(), name='add_teacher'),
    path('teachers/edit/<int:id>/', views.TeacherManagementView.as_view(), name='edit_teacher'),
    path('teachers/delete/<int:id>/', views.TeacherDeleteView.as_view(), name='delete_teacher'),  
 
      
    path('teacherswithcourses/add/', views.TeacherAvailabilityAndCoursesView.as_view(), name='add_edit_teacher_with_courses'),
    path('teacherswithcourses/edit/<int:id>/', views.TeacherAvailabilityAndCoursesView.as_view(), name='add_edit_teacher_with_courses'),
    # path('teacherswithcourses/delete/<int:pk>/', views.delete_teacher_with_courses_view, name='delete_teacher_with_courses'),  
      
    path('courses/', views.CoursesListView.as_view(), name='courses_management'),
    path('courses/add/', views.CourseCreateView.as_view(), name='add_course'),
    path('courses/<int:id>/edit/', views.CourseUpdateView.as_view(), name='edit_course'),
    path('courses/delete/<int:id>/', views.CourseDeleteView.as_view(), name='delete_course'),
    
    
    path('rooms/', views.RoomsListView.as_view(), name='rooms_management'),
    path('rooms/add/', views.RoomCreateView.as_view(), name='add_room'),
    path('rooms/edit/<int:id>/', views.RoomUpdateView.as_view(), name='edit_room'),
    path('rooms/delete/<int:id>/', views.RoomDeleteView.as_view(), name='delete_room'),
    
    path('departments/', views.DepartmentsListView.as_view(), name='departments_management'),
    path('departments/add/', views.DepartmentCreateView.as_view(), name='add_department'),
    path('departments/edit/<int:id>/', views.DepartmentUpdateView.as_view(), name='edit_department'),
    path('departments/delete/<int:id>/', views.DepartmentDeleteView.as_view(), name='delete_department'),
    
    # path('program/add/', views.AddAndEditProgramView.as_view(), name='add_program'),
    # path('program/edit/<int:id>/', views.AddAndEditProgramView.as_view(), name='edit_program'),
    
    path('programs/add/', views.AddProgramLevelView.as_view(), name='add_program'),
    path('programs/edit/<int:id>/',views.EditProgramLevelView.as_view(), name='edit_program'),
    path('programs/delete/<int:id>/',views.DeleteProgramLevelView.as_view(), name='delete_program'),
    
    path('timetable/', views.TimeTableSettingsView.as_view(), name='schedule_creation'),
    path('periods/', views.PeriodsView.as_view(), name='management_periods'),
    
    path('groups/', views.GroupsView.as_view(), name='groups_management'),
]