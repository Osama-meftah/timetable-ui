# filters.py
import django_filters
from .models import *

class LectureFilter(django_filters.FilterSet):
    program = django_filters.NumberFilter(field_name='fk_distribution__fk_group__fk_level__fk_program__id', lookup_expr='exact')

    class Meta:
        model = Lecture
        fields = ['program']

class SubjectFilter(django_filters.FilterSet):
    term = django_filters.CharFilter(field_name='term', lookup_expr='icontains')
    subject = django_filters.CharFilter(field_name='subject_name', lookup_expr='icontains')

    class Meta:
        model = Subject
        fields = ['term','subject']

class GroupFilter(django_filters.FilterSet):
    group=django_filters.CharFilter(field_name='group_name', lookup_expr='icontains')
    program = django_filters.NumberFilter(field_name='fk_level__fk_program__id', lookup_expr='exact')

    class Meta:
        model=Group
        fields=['group','program']

class TeacherFilter(django_filters.FilterSet):
    teacher=django_filters.CharFilter(field_name='teacher_name', lookup_expr='icontains')

    class Mata:
        model=Teacher
        fields=['tacher']

class DistributionFilter(django_filters.FilterSet):
    teacher=django_filters.CharFilter(field_name='fk_teacher__teacher_name', lookup_expr='icontains')
    teacherId=django_filters.NumberFilter(field_name='fk_teacher__id', lookup_expr='exact')

    class Mata:
        model=Distribution
        fields=['teacher']

class TeacherTimeFilter(django_filters.FilterSet):
    teacher=django_filters.CharFilter(field_name='fk_teacher__id', lookup_expr='icontains')

    class Mata:
        model=TeacherTime
        fields=['teacher']
