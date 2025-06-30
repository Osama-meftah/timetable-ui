from django.contrib import admin
from .models import Program, Hall,Department, Level, Group, Subject, Teacher, Today, Period, TeacherTime, Distribution, Table, Lecture

admin.site.register(Program)
admin.site.register(Hall)
admin.site.register(Level)
admin.site.register(Group)
admin.site.register(Subject)
admin.site.register(Teacher)
admin.site.register(Today)
admin.site.register(Period)
admin.site.register(TeacherTime)
admin.site.register(Distribution)
admin.site.register(Table)
admin.site.register(Lecture)
admin.site.register(Department)
